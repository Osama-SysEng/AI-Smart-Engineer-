from app.domain.projects.contracts import ProjectSnapshot
from app.domain.projects.policies import approval_required
from app.domain.projects.service import display_label, is_terminal

def test_projects_contract_and_policy():
    snapshot = ProjectSnapshot(identifier="projects-001", status="ACTIVE", tenant_id="tenant-1", correlation_id="req-projects")
    assert display_label(snapshot) == "projects-001 · ACTIVE"
    assert is_terminal("COMPLETED")
    assert approval_required("ERP_WRITE")
    assert not approval_required("READ")
