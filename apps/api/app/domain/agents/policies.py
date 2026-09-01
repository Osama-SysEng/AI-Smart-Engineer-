SENSITIVE_ACTIONS = {"ERP_WRITE", "DOCUMENT_DELETE", "MODEL_ROUTE_CHANGE", "EXPORT_EVIDENCE"}

def approval_required(action: str, risk: str = "LOW") -> bool:
    return action.upper() in SENSITIVE_ACTIONS or risk.upper() in {"HIGH", "CRITICAL"}

def may_access_tenant(request_tenant: str, resource_tenant: str) -> bool:
    return bool(request_tenant) and request_tenant == resource_tenant
