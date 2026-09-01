"""Approval bounded context: human-in-the-loop high-impact decisions."""
from .contracts import ApprovalSnapshot
from .policies import approval_required

__all__ = ["ApprovalSnapshot", "approval_required"]
