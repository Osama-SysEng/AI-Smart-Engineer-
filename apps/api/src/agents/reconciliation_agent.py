"""Reconciliation Agent - handles cross-source comparison."""
from typing import Dict, List

from src.agents.base import BaseAgent
from src.core.logging import get_logger

logger = get_logger(__name__)


class ReconciliationAgent(BaseAgent):
    """Agent for reconciliation and variance analysis."""

    def __init__(self):
        super().__init__(
            name="ReconciliationAgent",
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "run_reconciliation",
                        "description": "Run reconciliation between sources",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "project_id": {"type": "string"},
                                "sources": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["project_id", "sources"],
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "analyze_variance",
                        "description": "Analyze variance root cause",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "item_code": {"type": "string"},
                                "sources": {"type": "object"},
                            },
                            "required": ["item_code", "sources"],
                        },
                    },
                },
            ],
        )

    async def execute(self, intent: str, context: Dict, user_id: str) -> Dict:
        messages = [
            {"role": "system", "content": self.build_system_prompt()},
            {"role": "user", "content": f"Intent: {intent}\nContext: {context}"},
        ]

        response = await self.call_llm(messages, tools=self.tools, model=context.get("model_override"))

        return {
            "agent": self.name,
            "response": response["content"],
            "tools_used": [],
            "confidence": 0.88,
            "evidence": [],
            "requires_review": True,  # Reconciliation always needs review
        }
