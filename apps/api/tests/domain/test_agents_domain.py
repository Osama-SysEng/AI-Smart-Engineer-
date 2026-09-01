from app.domain.agents.contracts import AgentSnapshot
from app.domain.agents.policies import approval_required
from app.domain.agents.service import display_label, is_terminal

def test_agents_contract_and_policy():
    snapshot = AgentSnapshot(identifier="agents-001", status="ACTIVE", tenant_id="tenant-1", correlation_id="req-agents")
    assert display_label(snapshot) == "agents-001 · ACTIVE"
    assert is_terminal("COMPLETED")
    assert approval_required("ERP_WRITE")
    assert not approval_required("READ")
