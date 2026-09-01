from .contracts import ErpSnapshot

def display_label(snapshot: ErpSnapshot) -> str:
    return f"{snapshot.identifier} · {snapshot.status}"

def is_terminal(status: str) -> bool:
    return status.upper() in {"ARCHIVED", "COMPLETED", "FAILED", "REJECTED"}
