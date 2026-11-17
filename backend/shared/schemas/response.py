from datetime import datetime
from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, Field

T = TypeVar("T")

class PaginationMeta(BaseModel):
    page: int
    limit: int
    total_items: int
    total_pages: int

class ResponseMetadata(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StandardResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Success"
    data: Optional[T] = None
    metadata: ResponseMetadata = Field(default_factory=ResponseMetadata)
    pagination: Optional[PaginationMeta] = None
