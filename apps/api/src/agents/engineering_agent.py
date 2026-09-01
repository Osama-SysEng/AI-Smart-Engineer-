"""Engineering Agent - handles engineering data analysis."""
from typing import Dict, List

from src.agents.base import BaseAgent
from src.core.logging import get_logger

logger = get_logger(__name__)


class EngineeringAgent(BaseAgent):
    """Agent for engineering data and analysis."""

    def __init__(self):
        super().__init__(
            name="EngineeringAgent",
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "query_engineering_data",
                        "description": "Query engineering items and materials",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "project_id": {"type": "string"},
                                "site_id": {"type": "string"},
                                "item_code": {"type": "string"},
                                "category": {"type": "string"},
                            },
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "compare_revisions",
                        "description": "Compare document revisions",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "document_id": {"type": "string"},
                                "rev1": {"type": "string"},
                                "rev2": {"type": "string"},
                            },
                            "required": ["document_id"],
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
            "confidence": 0.85,
            "evidence": [],
            "requires_review": False,
        }
