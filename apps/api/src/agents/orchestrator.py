"""Agent Orchestrator - manages agent selection, planning, and execution."""
import json
from typing import Dict, List, Optional

from src.agents.base import BaseAgent
from src.agents.document_agent import DocumentAgent
from src.agents.engineering_agent import EngineeringAgent
from src.agents.reconciliation_agent import ReconciliationAgent
from src.agents.assistant_agent import AssistantAgent
from src.agents.devops_agent import DevOpsAgent
from src.agents.quality_agent import QualityAgent
from src.agents.security_agent import SecurityAgent
from src.agents.data_agent import DataAgent
from src.agents.sap_agent import SAPAgent
from src.agents.reporting_agent import ReportingAgent
from src.agents.anomaly_agent import AnomalyAgent
from src.agents.validation_agent import ValidationAgent
from src.ai.llm_provider import LLMRouter
from src.core.logging import get_logger
from src.core.exceptions import AIProviderError

logger = get_logger(__name__)


class AgentOrchestrator:
    """Orchestrates AI agents based on user intent."""

    def __init__(self):
        self.agents = {
            "document": DocumentAgent(),
            "engineering": EngineeringAgent(),
            "reconciliation": ReconciliationAgent(),
            "validation": ValidationAgent(),
            "anomaly": AnomalyAgent(),
            "reporting": ReportingAgent(),
            "sap": SAPAgent(),
            "data": DataAgent(),
            "security": SecurityAgent(),
            "quality": QualityAgent(),
            "devops": DevOpsAgent(),
            "assistant": AssistantAgent(),
        }
        self.llm_router = LLMRouter()
        self.logger = get_logger(__name__)

    async def process_request(self, message: str, user_id: str, context: Dict = None, project_id: str = None, site_id: str = None, model_override: str = None) -> Dict:
        """Process user request through the orchestrator."""
        context = context or {}
        if project_id:
            context["project_id"] = project_id
        if site_id:
            context["site_id"] = site_id

        # Step 1: Understand intent
        intent_analysis = await self._analyze_intent(message, context)
        self.logger.info("Intent analyzed", intent=intent_analysis["intent"], confidence=intent_analysis["confidence"])

        # Step 2: Plan execution
        plan = await self._create_plan(intent_analysis, context)
        self.logger.info("Plan created", steps=len(plan["steps"]))

        # Step 3: Execute plan
        results = []
        for step in plan["steps"]:
            agent_name = step["agent"]
            agent = self.agents.get(agent_name, self.agents["assistant"])

            self.logger.info("Executing step", agent=agent_name, step=step["description"])
            result = await agent.execute(
                intent=step["intent"],
                context={**context, **step.get("context", {}), "model_override": model_override},
                user_id=user_id,
            )
            results.append(result)

        # Step 4: Synthesize response
        final_response = await self._synthesize_response(message, results, intent_analysis)

        return {
            "response": final_response["content"],
            "intent": intent_analysis["intent"],
            "tools_used": list(set(t for r in results for t in r.get("tools_used", []))),
            "data_sources": [],
            "confidence": min(r.get("confidence", 1.0) for r in results) if results else 1.0,
            "requires_approval": any(r.get("requires_review", False) for r in results),
            "suggested_actions": final_response.get("suggested_actions", []),
            "trace_id": intent_analysis.get("trace_id", ""),
            "latency_ms": 0,
            "cost_estimate": sum(r.get("cost", 0) for r in results),
        }

    async def _analyze_intent(self, message: str, context: Dict) -> Dict:
        """Analyze user intent."""
        import uuid
        trace_id = str(uuid.uuid4())

        system_prompt = """You are an intent classifier for an engineering AI platform.
Classify the user intent into one of these categories:
- document_analysis: analyzing documents, drawings, PDFs
- data_extraction: extracting data from files
- reconciliation: comparing data between sources
- report_generation: generating reports
- anomaly_detection: finding anomalies
- sap_query: querying SAP data
- general_question: general engineering question
- task_creation: creating tasks
- approval_request: requesting approval

Return JSON with: intent, confidence (0-1), entities (extracted), complexity (low/medium/high), sensitivity (low/medium/high)"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ]

        try:
            response = await self.llm_router.route(messages, complexity="low")
            # Parse JSON from response
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()

            analysis = json.loads(content)
            analysis["trace_id"] = trace_id
            return analysis
        except Exception as e:
            self.logger.error("Intent analysis failed", error=str(e))
            return {
                "intent": "general_question",
                "confidence": 0.5,
                "entities": {},
                "complexity": "medium",
                "sensitivity": "low",
                "trace_id": trace_id,
            }

    async def _create_plan(self, intent_analysis: Dict, context: Dict) -> Dict:
        """Create execution plan."""
        intent = intent_analysis["intent"]

        plans = {
            "document_analysis": {
                "steps": [
                    {"agent": "document", "description": "Search and analyze documents", "intent": intent_analysis.get("entities", {}).get("document_query", "")},
                    {"agent": "assistant", "description": "Summarize findings", "intent": "summarize"},
                ]
            },
            "reconciliation": {
                "steps": [
                    {"agent": "reconciliation", "description": "Run reconciliation", "intent": "compare sources"},
                    {"agent": "assistant", "description": "Generate report", "intent": "report"},
                ]
            },
            "data_extraction": {
                "steps": [
                    {"agent": "document", "description": "Extract data from documents", "intent": "extract"},
                    {"agent": "validation", "description": "Validate extracted values", "intent": "validate"},
                    {"agent": "data", "description": "Normalize and analyze data", "intent": "normalize"},
                ]
            },
            "anomaly_detection": {
                "steps": [
                    {"agent": "data", "description": "Profile source data", "intent": "profile"},
                    {"agent": "anomaly", "description": "Detect anomalies", "intent": "detect anomalies"},
                    {"agent": "reporting", "description": "Prepare evidence report", "intent": "report"},
                ]
            },
            "report_generation": {
                "steps": [{"agent": "reporting", "description": "Generate verified report", "intent": "report"}]
            },
            "sap_query": {
                "steps": [{"agent": "sap", "description": "Query SAP safely", "intent": "sap query"}]
            },
            "task_creation": {
                "steps": [{"agent": "assistant", "description": "Prepare task", "intent": "create task"}]
            },
            "general_question": {
                "steps": [
                    {"agent": "assistant", "description": "Answer question", "intent": intent_analysis.get("entities", {}).get("question", "")},
                ]
            },
        }

        return plans.get(intent, plans["general_question"])

    async def _synthesize_response(self, original_message: str, results: List[Dict], intent_analysis: Dict) -> Dict:
        """Synthesize final response from agent results."""
        combined = "\n\n".join([f"Agent {r['agent']}: {r['response']}" for r in results])

        system_prompt = """You are the response synthesizer for an engineering AI platform.
Synthesize the agent results into a clear, actionable response.
Always:
1. State facts clearly with evidence
2. Highlight any variances or anomalies
3. Suggest next actions
4. Flag if human review is needed
5. Never make up data"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Original question: {original_message}\n\nAgent results:\n{combined}"},
        ]

        response = await self.llm_router.route(messages, complexity="medium")

        return {
            "content": response.content,
            "suggested_actions": [],
        }

    async def run_analysis(self, analysis_type: str, data: Dict, user_id: str) -> Dict:
        """Run specific analysis."""
        return await self.process_request(
            message=f"Run {analysis_type} analysis",
            user_id=user_id,
            context={"analysis_type": analysis_type, "data": data},
        )
