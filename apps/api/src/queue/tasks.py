"""Celery tasks."""
import asyncio
from celery import shared_task
from sqlalchemy.ext.asyncio import AsyncSession

from src.queue.celery_app import celery_app
from src.core.logging import get_logger
from src.db.session import async_session
from src.services.document_processor import DocumentProcessor
from src.services.extraction_engine import ExtractionEngine
from src.services.reconciliation_engine import ReconciliationEngine
from src.services.report_generator import ReportGenerator
from src.integrations.sap.adapter import SAPAdapter
from src.agents.orchestrator import AgentOrchestrator

logger = get_logger(__name__)


def get_async_db():
    return async_session()


@shared_task(bind=True, max_retries=3)
def process_document_task(self, document_id: str):
    """Process uploaded document."""
    logger.info("Processing document", document_id=document_id)
    try:
        processor = DocumentProcessor()
        asyncio.run(processor.process(document_id))
        return {"status": "completed", "document_id": document_id}
    except Exception as exc:
        logger.error("Document processing failed", error=str(exc), document_id=document_id)
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def run_extraction_task(self, run_id: str, model_override: str | None = None):
    """Run AI extraction."""
    logger.info("Running extraction", run_id=run_id)
    try:
        engine = ExtractionEngine()
        asyncio.run(engine.run(run_id, model_override))
        return {"status": "completed", "run_id": run_id}
    except Exception as exc:
        logger.error("Extraction failed", error=str(exc), run_id=run_id)
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def run_reconciliation_task(self, run_id: str):
    """Run reconciliation."""
    logger.info("Running reconciliation", run_id=run_id)
    try:
        engine = ReconciliationEngine()
        asyncio.run(engine.run(run_id))
        return {"status": "completed", "run_id": run_id}
    except Exception as exc:
        logger.error("Reconciliation failed", error=str(exc), run_id=run_id)
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=2)
def generate_report_task(self, report_type: str, project_id: str | None = None, site_id: str | None = None, date_from: str | None = None, date_to: str | None = None, user_id: str | None = None):
    """Generate report."""
    logger.info("Generating report", report_type=report_type)
    try:
        generator = ReportGenerator()
        asyncio.run(generator.generate(report_type, project_id, site_id, date_from, date_to, user_id))
        return {"status": "completed", "report_type": report_type}
    except Exception as exc:
        logger.error("Report generation failed", error=str(exc))
        raise self.retry(exc=exc, countdown=120)


@shared_task(bind=True, max_retries=5)
def sap_sync_task(self, record_id: str, dry_run: bool = True):
    """Sync with SAP."""
    logger.info("SAP sync", record_id=record_id, dry_run=dry_run)
    try:
        adapter = SAPAdapter()
        asyncio.run(adapter.sync_record(record_id, dry_run))
        return {"status": "completed", "record_id": record_id}
    except Exception as exc:
        logger.error("SAP sync failed", error=str(exc), record_id=record_id)
        raise self.retry(exc=exc, countdown=300)


@shared_task(bind=True, max_retries=2)
def ai_analysis_task(self, analysis_type: str, data: dict, user_id: str):
    """Run AI analysis."""
    logger.info("AI analysis", analysis_type=analysis_type)
    try:
        orchestrator = AgentOrchestrator()
        result = asyncio.run(orchestrator.run_analysis(analysis_type, data, user_id))
        return {"status": "completed", "result": result}
    except Exception as exc:
        logger.error("AI analysis failed", error=str(exc))
        raise self.retry(exc=exc, countdown=60)


@shared_task
def cleanup_old_files():
    """Remove temporary files older than the configured retention period."""
    from pathlib import Path
    from datetime import datetime, timedelta, timezone
    settings = __import__("src.core.config", fromlist=["get_settings"]).get_settings()
    root = Path(settings.STORAGE_PATH)
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    removed = 0
    if root.exists():
        for path in root.rglob("*"):
            if path.is_file() and datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc) < cutoff:
                path.unlink(missing_ok=True)
                removed += 1
    logger.info("Cleanup completed", removed=removed)
    return {"status": "completed", "removed": removed}


@shared_task
def send_notification_task(user_id: str, title: str, message: str, severity: str = "info"):
    """Persist an in-app notification."""
    from src.db.models.notification import Notification
    async def _create():
        async with async_session() as db:
            db.add(Notification(user_id=user_id, title=title, message=message, severity=severity, read=False))
            await db.commit()
    asyncio.run(_create())
    logger.info("Notification persisted", user_id=user_id, title=title)
    return {"status": "completed", "user_id": user_id}
