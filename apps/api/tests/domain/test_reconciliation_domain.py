from app.domain.reconciliation.contracts import ReconciliationSnapshot
from app.domain.reconciliation.policies import approval_required
from app.domain.reconciliation.service import display_label, is_terminal

def test_reconciliation_contract_and_policy():
    snapshot = ReconciliationSnapshot(identifier="reconciliation-001", status="ACTIVE", tenant_id="tenant-1", correlation_id="req-reconciliation")
    assert display_label(snapshot) == "reconciliation-001 · ACTIVE"
    assert is_terminal("COMPLETED")
    assert approval_required("ERP_WRITE")
    assert not approval_required("READ")
