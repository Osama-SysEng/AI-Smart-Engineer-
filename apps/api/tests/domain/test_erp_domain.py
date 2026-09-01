from app.domain.erp.contracts import ErpSnapshot
from app.domain.erp.policies import approval_required
from app.domain.erp.service import display_label, is_terminal

def test_erp_contract_and_policy():
    snapshot = ErpSnapshot(identifier="erp-001", status="ACTIVE", tenant_id="tenant-1", correlation_id="req-erp")
    assert display_label(snapshot) == "erp-001 · ACTIVE"
    assert is_terminal("COMPLETED")
    assert approval_required("ERP_WRITE")
    assert not approval_required("READ")
