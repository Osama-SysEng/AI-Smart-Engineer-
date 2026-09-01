"""Document Agent - handles document understanding and extraction."""
from typing import Dict, List

from src.agents.base import BaseAgent
from src.core.logging import get_logger

logger = get_logger(__name__)


class DocumentAgent(BaseAgent):
    """Agent for document processing and extraction."""

    def __init__(self):
        super().__init__(
            name="DocumentAgent",
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "search_documents",
                        "description": "Search for documents by criteria",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "project_id": {"type": "string"},
                                "site_id": {"type": "string"},
                                "file_type": {"type": "string"},
                                "status": {"type": "string"},
                            },
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "read_document",
                        "description": "Read document content and metadata",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "document_id": {"type": "string"},
                            },
                            "required": ["document_id"],
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "extract_data",
                        "description": "Extract structured data from document",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "document_id": {"type": "string"},
                                "entity_types": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["document_id"],
                        },
                    },
                },
            ],
        )

    async def execute(self, intent: str, context: Dict, user_id: str) -> Dict:
        """Execute document agent."""
        messages = [
            {"role": "system", "content": self.build_system_prompt()},
            {"role": "user", "content": f"Intent: {intent}\nContext: {context}"},
        ]

        response = await self.call_llm(messages, tools=self.tools, model=context.get("model_override"))

        return {
            "agent": self.name,
            "response": response["content"],
            "tools_used": [t["function"]["name"] for t in self.tools],
            "confidence": 0.9,
            "evidence": [],
            "requires_review": False,
        }
