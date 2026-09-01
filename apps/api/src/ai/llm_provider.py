"""LLM Provider abstraction with routing, fallback, and cost tracking."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime

from src.core.config import get_settings
from src.core.logging import get_logger
from src.core.exceptions import AIProviderError

logger = get_logger(__name__)


class LLMResponse:
    """Standardized LLM response."""
    def __init__(self, content: str, model: str, provider: str, tokens_in: int = 0, tokens_out: int = 0, latency_ms: int = 0, cost: float = 0.0, tool_calls: List[Dict] = None):
        self.content = content
        self.model = model
        self.provider = provider
        self.tokens_in = tokens_in
        self.tokens_out = tokens_out
        self.total_tokens = tokens_in + tokens_out
        self.latency_ms = latency_ms
        self.cost = cost
        self.tool_calls = tool_calls or []
        self.timestamp = datetime.utcnow()


class BaseLLMProvider(ABC):
    """Base class for LLM providers."""

    def __init__(self, name: str):
        self.name = name
        self.settings = get_settings()

    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], model: str = None, temperature: float = 0.7, max_tokens: int = 4000, tools: List[Dict] = None) -> LLMResponse:
        pass

    @abstractmethod
    async def embed(self, texts: List[str], model: str = None) -> List[List[float]]:
        pass

    def calculate_cost(self, tokens_in: int, tokens_out: int, model: str) -> float:
        """Calculate estimated cost in USD."""
        rates = {
            "gpt-4o": {"in": 0.005, "out": 0.015},
            "gpt-4o-mini": {"in": 0.00015, "out": 0.0006},
            "claude-3-5-sonnet": {"in": 0.003, "out": 0.015},
            "claude-3-haiku": {"in": 0.00025, "out": 0.00125},
            "gemini-1.5-pro": {"in": 0.0035, "out": 0.0105},
            "deepseek-chat": {"in": 0.00014, "out": 0.00028},
        }
        rate = rates.get(model, {"in": 0.01, "out": 0.03})
        return (tokens_in * rate["in"] + tokens_out * rate["out"]) / 1000


class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider."""

    def __init__(self):
        super().__init__("openai")
        self.client = None

    def _get_client(self):
        if not self.settings.OPENAI_API_KEY:
            raise AIProviderError("OpenAI API key is not configured")
        if self.client is None:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)
        return self.client

    async def chat(self, messages, model=None, temperature=0.7, max_tokens=4000, tools=None):
        import time
        start = time.time()
        model = model or "gpt-4o"

        try:
            response = await self._get_client().chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=tools,
            )
            latency = int((time.time() - start) * 1000)
            content = response.choices[0].message.content or ""
            tool_calls = []
            if response.choices[0].message.tool_calls:
                tool_calls = [{"name": tc.function.name, "arguments": tc.function.arguments} for tc in response.choices[0].message.tool_calls]

            return LLMResponse(
                content=content,
                model=model,
                provider=self.name,
                tokens_in=response.usage.prompt_tokens,
                tokens_out=response.usage.completion_tokens,
                latency_ms=latency,
                cost=self.calculate_cost(response.usage.prompt_tokens, response.usage.completion_tokens, model),
                tool_calls=tool_calls,
            )
        except Exception as e:
            logger.error("OpenAI error", error=str(e))
            raise AIProviderError(f"OpenAI failed: {str(e)}")

    async def embed(self, texts, model=None):
        model = model or "text-embedding-3-large"
        response = await self._get_client().embeddings.create(model=model, input=texts)
        return [item.embedding for item in response.data]


class OpenAICompatibleProvider(BaseLLMProvider):
    """Provider using OpenAI-compatible chat API (DeepSeek-compatible endpoint)."""

    def __init__(self, name: str, api_key: str | None, base_url: str, default_model: str):
        super().__init__(name)
        self.api_key = api_key
        self.base_url = base_url
        self.default_model = default_model
        self.client = None

    def _get_client(self):
        if not self.api_key:
            raise AIProviderError(f"{self.name} API key is not configured")
        if self.client is None:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        return self.client

    async def chat(self, messages, model=None, temperature=0.7, max_tokens=4000, tools=None):
        import time
        start = time.time()
        model = model or self.default_model
        try:
            response = await self._get_client().chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=tools,
            )
            usage = response.usage
            tokens_in = getattr(usage, "prompt_tokens", 0) if usage else 0
            tokens_out = getattr(usage, "completion_tokens", 0) if usage else 0
            message = response.choices[0].message
            return LLMResponse(
                content=message.content or "",
                model=model,
                provider=self.name,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                latency_ms=int((time.time() - start) * 1000),
                cost=self.calculate_cost(tokens_in, tokens_out, model),
                tool_calls=[{"name": tc.function.name, "arguments": tc.function.arguments} for tc in (message.tool_calls or [])],
            )
        except Exception as exc:
            logger.error(f"{self.name} error", error=str(exc))
            raise AIProviderError(f"{self.name} failed: {exc}") from exc

    async def embed(self, texts, model=None):
        raise AIProviderError(f"{self.name} embeddings are not configured")


class GoogleProvider(BaseLLMProvider):
    """Google Gemini provider using google-generativeai."""

    def __init__(self):
        super().__init__("google")
        self.configured = False

    def _configure(self):
        if self.configured:
            return
        if not self.settings.GOOGLE_API_KEY:
            raise AIProviderError("Google API key is not configured")
        import google.generativeai as genai
        genai.configure(api_key=self.settings.GOOGLE_API_KEY)
        self.configured = True

    async def chat(self, messages, model=None, temperature=0.7, max_tokens=4000, tools=None):
        import asyncio
        import time
        self._configure()
        import google.generativeai as genai
        model_name = model or "gemini-1.5-flash"
        system = "\n".join(m["content"] for m in messages if m.get("role") == "system")
        history = [{"role": "user" if m["role"] in {"user", "system"} else "model", "parts": [m["content"]]} for m in messages if m.get("role") != "system"]
        prompt = history[-1]["parts"][0] if history else ""
        previous = history[:-1]

        def call():
            gm = genai.GenerativeModel(model_name, system_instruction=system or None)
            chat = gm.start_chat(history=previous)
            return chat.send_message(prompt, generation_config={"temperature": temperature, "max_output_tokens": max_tokens})

        start = time.time()
        try:
            response = await asyncio.to_thread(call)
            text = getattr(response, "text", "")
            usage = getattr(response, "usage_metadata", None)
            tokens_in = getattr(usage, "prompt_token_count", 0) if usage else 0
            tokens_out = getattr(usage, "candidates_token_count", 0) if usage else 0
            return LLMResponse(text, model_name, self.name, tokens_in, tokens_out, int((time.time()-start)*1000), self.calculate_cost(tokens_in, tokens_out, model_name))
        except Exception as exc:
            logger.error("Google error", error=str(exc))
            raise AIProviderError(f"Google failed: {exc}") from exc

    async def embed(self, texts, model=None):
        self._configure()
        import google.generativeai as genai
        result = await __import__("asyncio").to_thread(lambda: [genai.embed_content(model=model or "models/text-embedding-004", content=t, task_type="retrieval_document")["embedding"] for t in texts])
        return result


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider."""

    def __init__(self):
        super().__init__("anthropic")
        self.client = None

    def _get_client(self):
        if not self.settings.ANTHROPIC_API_KEY:
            raise AIProviderError("Anthropic API key is not configured")
        if self.client is None:
            from anthropic import AsyncAnthropic
            self.client = AsyncAnthropic(api_key=self.settings.ANTHROPIC_API_KEY)
        return self.client

    async def chat(self, messages, model=None, temperature=0.7, max_tokens=4000, tools=None):
        import time
        start = time.time()
        model = model or "claude-3-5-sonnet-20241022"

        try:
            # Convert messages to Anthropic format
            system_msg = ""
            user_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    system_msg = msg["content"]
                else:
                    user_messages.append({"role": msg["role"], "content": msg["content"]})

            response = await self._get_client().messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_msg,
                messages=user_messages,
            )
            latency = int((time.time() - start) * 1000)
            content = ""
            for block in response.content:
                if block.type == "text":
                    content += block.text

            # Estimate tokens (Anthropic doesn't return exact counts)
            tokens_in = response.usage.input_tokens
            tokens_out = response.usage.output_tokens

            return LLMResponse(
                content=content,
                model=model,
                provider=self.name,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                latency_ms=latency,
                cost=self.calculate_cost(tokens_in, tokens_out, model),
            )
        except Exception as e:
            logger.error("Anthropic error", error=str(e))
            raise AIProviderError(f"Anthropic failed: {str(e)}")

    async def embed(self, texts, model=None):
        raise AIProviderError("Anthropic does not support embeddings")


class LocalProvider(BaseLLMProvider):
    """Local Ollama provider."""

    def __init__(self):
        super().__init__("local")

    async def chat(self, messages, model=None, temperature=0.7, max_tokens=4000, tools=None):
        import time
        import httpx
        start = time.time()
        model = model or "llama3"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.settings.LOCAL_LLM_URL}/api/chat",
                    json={
                        "model": model,
                        "messages": messages,
                        "stream": False,
                        "options": {"temperature": temperature, "num_predict": max_tokens},
                    },
                    timeout=120.0,
                )
                response.raise_for_status()
                data = response.json()
                latency = int((time.time() - start) * 1000)
                content = data.get("message", {}).get("content", "")

                return LLMResponse(
                    content=content,
                    model=model,
                    provider=self.name,
                    tokens_in=0,
                    tokens_out=0,
                    latency_ms=latency,
                    cost=0.0,
                )
        except Exception as e:
            logger.error("Local LLM error", error=str(e))
            raise AIProviderError(f"Local LLM failed: {str(e)}")

    async def embed(self, texts, model=None):
        import httpx
        model = model or "llama3"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.settings.LOCAL_LLM_URL}/api/embeddings",
                json={"model": model, "prompt": texts[0]},
            )
            data = response.json()
            return [data.get("embedding", [])]


class LLMRouter:
    """Intelligent LLM router with fallback."""

    def __init__(self):
        self.settings = get_settings()
        self.providers = {
            "openai": OpenAIProvider(),
            "anthropic": AnthropicProvider(),
            "google": GoogleProvider(),
            "deepseek": OpenAICompatibleProvider(
                "deepseek",
                self.settings.DEEPSEEK_API_KEY,
                "https://api.deepseek.com",
                "deepseek-chat",
            ),
            "local": LocalProvider(),
        }
        self.logger = get_logger(__name__)

    async def route(self, messages, complexity="medium", sensitivity="low", latency_required="normal", cost_limit=None, preferred_provider=None, model=None):
        """Route request with configured-provider filtering and deterministic fallback order."""
        requested = preferred_provider or self.settings.DEFAULT_AI_PROVIDER
        if requested not in self.providers:
            requested = "local" if sensitivity == "high" and self.settings.LOCAL_MODEL_ENABLED else "openai"

        order = []
        if sensitivity == "high" and self.settings.LOCAL_MODEL_ENABLED:
            order.append("local")
        if requested in self.providers:
            order.append(requested)
        if complexity == "high":
            order.extend(["openai", "anthropic", "google", "deepseek"])
        configured_fallback = self.settings.FALLBACK_PROVIDER
        if configured_fallback in self.providers:
            order.append(configured_fallback)
        if self.settings.LOCAL_MODEL_ENABLED:
            order.append("local")

        providers_to_try = []
        for name in order:
            provider = self.providers.get(name)
            if provider is None or provider in providers_to_try:
                continue
            if name == "openai" and not self.settings.OPENAI_API_KEY:
                continue
            if name == "anthropic" and not self.settings.ANTHROPIC_API_KEY:
                continue
            if name == "google" and not self.settings.GOOGLE_API_KEY:
                continue
            if name == "deepseek" and not self.settings.DEEPSEEK_API_KEY:
                continue
            if name == "local" and not self.settings.LOCAL_MODEL_ENABLED:
                continue
            providers_to_try.append(provider)

        if not providers_to_try:
            raise AIProviderError("No configured AI providers available")

        last_error = None
        for provider in providers_to_try:
            try:
                selected_model = model
                if provider.name == "openai" and not selected_model:
                    selected_model = self.settings.DEFAULT_AI_MODEL
                response = await provider.chat(messages, model=selected_model)
                self.logger.info("Provider succeeded", provider=provider.name, model=response.model, latency=response.latency_ms, cost=response.cost)
                return response
            except Exception as exc:
                last_error = exc
                self.logger.warning("Provider failed, trying fallback", provider=provider.name, error=str(exc))

        raise AIProviderError(f"All configured providers failed. Last error: {last_error}")

    async def embed(self, texts, provider_name="openai", model=None):
        provider = self.providers.get(provider_name, self.providers["openai"])
        return await provider.embed(texts, model)
