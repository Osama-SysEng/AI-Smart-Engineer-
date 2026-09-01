"""Common schemas."""
from typing import Generic, List, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class ErrorResponse(BaseModel):
    code: str
    message: str
    request_id: str | None = None
    retryable: bool = False
    context: dict | None = None


class SuccessResponse(BaseModel):
    success: bool = True
    message: str | None = None
    data: dict | None = None
