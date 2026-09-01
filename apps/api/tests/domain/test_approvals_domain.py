from app.domain.approvals.contracts import ApprovalSnapshot
from app.domain.approvals.policies import approval_required
from app.domain.approvals.service import display_label, is_terminal

def test_approvals_contract_and_policy():
    snapshot = ApprovalSnapshot(identifier="approvals-001", status="ACTIVE", tenant_id="tenant-1", correlation_id="req-approvals")
    assert display_label(snapshot) == "approvals-001 · ACTIVE"
    assert is_terminal("COMPLETED")
    assert approval_required("ERP_WRITE")
    assert not approval_required("READ")
