"""Base agent class."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from src.core.logging import get_logger
from src.ai.llm_provider import LLMRouter

logger = get_logger(__name__)


class BaseAgent(ABC):
    """Base class for all AI agents."""

    def __init__(self, name: str, tools: List[Dict] = None, model_policy: str = "auto"):
        self.name = name
        self.tools = tools or []
        self.model_policy = model_policy
        self.llm_router = LLMRouter()
        self.logger = get_logger(f"agent.{name}")

    @abstractmethod
    async def execute(self, intent: str, context: Dict, user_id: str) -> Dict:
        """Execute agent logic."""
        pass

    def build_system_prompt(self) -> str:
        """Build system prompt for the agent."""
        return f"""You are the {self.name} agent in the AI Smart Engineer platform.
You are an engineering intelligence assistant. You must:
1. Always provide evidence-based answers
2. Never hallucinate data - if unsure, say "INSUFFICIENT_EVIDENCE"
3. Cite your sources
4. Provide confidence scores
5. Flag when human review is needed
6. Never execute actions without proper authorization
7. Respect data privacy and security policies
"""

    async def call_llm(self, messages: List[Dict], tools: List[Dict] = None, model: str = None) -> Dict:
        """Call LLM with routing."""
        response = await self.llm_router.route(
            messages=messages,
            preferred_provider=None,
            model=model,
        )
        return {
            "content": response.content,
            "model": response.model,
            "provider": response.provider,
            "tokens_in": response.tokens_in,
            "tokens_out": response.tokens_out,
            "cost": response.cost,
            "latency_ms": response.latency_ms,
            "tool_calls": response.tool_calls,
        }
