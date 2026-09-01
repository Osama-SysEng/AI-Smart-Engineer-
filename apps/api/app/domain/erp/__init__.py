"""Erp bounded context: read-safe integration and controlled outbox delivery."""
from .contracts import ErpSnapshot
from .policies import approval_required

__all__ = ["ErpSnapshot", "approval_required"]
