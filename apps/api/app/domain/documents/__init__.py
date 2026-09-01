"""Document bounded context: ingestion, extraction, retention, and evidence."""
from .contracts import DocumentSnapshot
from .policies import approval_required

__all__ = ["DocumentSnapshot", "approval_required"]
