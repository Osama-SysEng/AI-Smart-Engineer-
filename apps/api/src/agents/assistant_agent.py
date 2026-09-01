"""Assistant Agent - general engineering assistant."""
from typing import Dict, List

from src.agents.base import BaseAgent
from src.core.logging import get_logger

logger = get_logger(__name__)


class AssistantAgent(BaseAgent):
    """General AI Engineering Assistant."""

    def __init__(self):
        super().__init__(
            name="AssistantAgent",
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "search_documents",
                        "description": "Search documents",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"},
                                "project_id": {"type": "string"},
                            },
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "query_database",
                        "description": "Query engineering database",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"},
                                "table": {"type": "string"},
                            },
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "query_sap",
                        "description": "Query SAP data",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "table": {"type": "string"},
                                "filters": {"type": "object"},
                            },
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "generate_report",
                        "description": "Generate a report",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "report_type": {"type": "string"},
                                "project_id": {"type": "string"},
                            },
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "create_task",
                        "description": "Create a task",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "description": {"type": "string"},
                                "project_id": {"type": "string"},
                            },
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "request_approval",
                        "description": "Request approval for an action",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "action": {"type": "string"},
                                "reason": {"type": "string"},
                            },
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
            "confidence": 0.9,
            "evidence": [],
            "requires_review": False,
        }
