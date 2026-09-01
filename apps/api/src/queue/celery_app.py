"""Celery configuration."""
from celery import Celery
from src.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "ai_smart_engineer",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "src.queue.tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_routes={
        "src.queue.tasks.process_document_task": {"queue": "ocr"},
        "src.queue.tasks.run_extraction_task": {"queue": "extraction"},
        "src.queue.tasks.run_reconciliation_task": {"queue": "default"},
        "src.queue.tasks.generate_report_task": {"queue": "reports"},
        "src.queue.tasks.sap_sync_task": {"queue": "sap"},
        "src.queue.tasks.ai_analysis_task": {"queue": "ai"},
    },
    beat_schedule={
        "daily-reports": {
            "task": "src.queue.tasks.generate_report_task",
            "schedule": 86400.0,
            "args": ("daily",),
        },
        "cleanup-old-files": {
            "task": "src.queue.tasks.cleanup_old_files",
            "schedule": 3600.0,
        },
    },
)
