from app.domain.documents.contracts import DocumentSnapshot
from app.domain.documents.policies import approval_required
from app.domain.documents.service import display_label, is_terminal

def test_documents_contract_and_policy():
    snapshot = DocumentSnapshot(identifier="documents-001", status="ACTIVE", tenant_id="tenant-1", correlation_id="req-documents")
    assert display_label(snapshot) == "documents-001 · ACTIVE"
    assert is_terminal("COMPLETED")
    assert approval_required("ERP_WRITE")
    assert not approval_required("READ")
