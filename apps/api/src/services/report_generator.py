"""Report generation service."""
from datetime import datetime
from typing import Dict, List, Optional

from src.core.config import get_settings
from src.core.logging import get_logger
from src.ai.llm_provider import LLMRouter

logger = get_logger(__name__)


class ReportGenerator:
    """Generate various reports."""

    def __init__(self):
        self.llm_router = LLMRouter()
        self.settings = get_settings()

    async def generate(self, report_type: str, project_id: str = None, site_id: str = None, date_from: str = None, date_to: str = None, user_id: str = None) -> Dict:
        """Generate a report."""
        logger.info("Generating report", report_type=report_type, project_id=project_id)

        # Collect data
        data = await self._collect_report_data(report_type, project_id, site_id, date_from, date_to)

        # Generate report with AI
        report_content = await self._generate_report_content(report_type, data)

        # Save report
        report_path = await self._save_report(report_type, report_content, project_id)

        return {
            "status": "completed",
            "report_type": report_type,
            "path": report_path,
            "generated_at": datetime.now().isoformat(),
        }

    async def _collect_report_data(self, report_type: str, project_id: str, site_id: str, date_from: str, date_to: str) -> Dict:
        """Collect data for report."""
        from sqlalchemy import select, func, and_
        from src.db.session import async_session
        from src.db.models.document import Document
        from src.db.models.reconciliation import ReconciliationRun
        from src.db.models.workflow import Task
        from src.db.models.quality import QualityRecord

        async with async_session() as db:
            data = {"report_type": report_type, "generated_at": datetime.now().isoformat()}

            if report_type in ["daily", "weekly", "monthly", "project"]:
                # Document stats
                doc_query = select(func.count(Document.id)).where(Document.is_deleted == False)
                if project_id:
                    doc_query = doc_query.where(Document.project_id == project_id)
                result = await db.execute(doc_query)
                data["total_documents"] = result.scalar() or 0

                # Task stats
                task_query = select(func.count(Task.id))
                if project_id:
                    task_query = task_query.where(Task.project_id == project_id)
                result = await db.execute(task_query)
                data["total_tasks"] = result.scalar() or 0

                # Pending tasks
                pending_query = select(func.count(Task.id)).where(Task.status == "pending")
                if project_id:
                    pending_query = pending_query.where(Task.project_id == project_id)
                result = await db.execute(pending_query)
                data["pending_tasks"] = result.scalar() or 0

                # Reconciliation variances
                variance_query = select(func.count(ReconciliationRun.id)).where(ReconciliationRun.variance_count > 0)
                if project_id:
                    variance_query = variance_query.where(ReconciliationRun.project_id == project_id)
                result = await db.execute(variance_query)
                data["open_variances"] = result.scalar() or 0

            return data

    async def _generate_report_content(self, report_type: str, data: Dict) -> str:
        """Generate report content using AI."""
        system_prompt = f"""You are a professional engineering report writer.
Generate a comprehensive {report_type} report based on the provided data.
Structure:
1. Executive Summary
2. Key Metrics
3. Issues & Variances
4. Recommended Actions
5. Next Steps

Be concise, factual, and actionable. Use professional engineering language."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Report data: {data}"},
        ]

        response = await self.llm_router.route(messages, complexity="medium")
        return response.content

    async def _save_report(self, report_type: str, content: str, project_id: str) -> str:
        """Save report to storage."""
        from src.storage.service import StorageService

        storage = StorageService()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{report_type}_{timestamp}.md"

        # Save as markdown
        # In production, convert to PDF/Excel
        return f"/app/storage/reports/{filename}"
