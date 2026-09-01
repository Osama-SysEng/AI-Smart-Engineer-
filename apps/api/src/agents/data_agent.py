"""DataAgent."""
from typing import Dict
from src.agents.base import BaseAgent


class DataAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="DataAgent")

    async def execute(self, intent: str, context: Dict, user_id: str) -> Dict:
        messages = [
            {"role": "system", "content": self.build_system_prompt() + "\nSpecialty: Normalize, map, profile, and analyze structured engineering datasets."},
            {"role": "user", "content": f"Intent: {intent}\nContext: {context}"},
        ]
        response = await self.call_llm(messages, model=context.get("model_override"))
        return {
            "agent": self.name,
            "response": response["content"],
            "tools_used": response.get("tool_calls", []),
            "confidence": 0.8,
            "evidence": [],
            "requires_review": True,
            "provider": response.get("provider"),
            "model": response.get("model"),
            "cost": response.get("cost", 0),
        }
