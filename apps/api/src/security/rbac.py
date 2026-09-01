"""Role-Based Access Control."""
from fastapi import HTTPException, status

from src.db.models.user import User
from src.security.policy import evaluate_permission


def check_permission(user: User, resource: str, action: str) -> bool:
    return evaluate_permission(user, resource=resource, action=action).allowed


class PermissionChecker:
    def __init__(self, resource: str, action: str):
        self.resource = resource
        self.action = action

    def __call__(self, user: User) -> bool:
        if not check_permission(user, self.resource, self.action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {self.resource}:{self.action}"
            )
        return True
