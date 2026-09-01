"""SAPAgent."""
from typing import Dict
from src.agents.base import BaseAgent


class SAPAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="SAPAgent")

    async def execute(self, intent: str, context: Dict, user_id: str) -> Dict:
        messages = [
            {"role": "system", "content": self.build_system_prompt() + "\nSpecialty: Read and reconcile SAP data. Never write SAP without explicit approval and policy."},
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
