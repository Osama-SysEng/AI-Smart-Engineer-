from .contracts import ProjectSnapshot

def display_label(snapshot: ProjectSnapshot) -> str:
    return f"{snapshot.identifier} · {snapshot.status}"

def is_terminal(status: str) -> bool:
    return status.upper() in {"ARCHIVED", "COMPLETED", "FAILED", "REJECTED"}
