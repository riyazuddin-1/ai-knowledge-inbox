from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.content import ContentType, ContentStatus

class IngestRequest(BaseModel):
  type: ContentType
  data: str

class ContentResponse(BaseModel):
  id: int
  title: Optional[str]
  source: Optional[str]
  type: ContentType
  status: ContentStatus
  created_at: datetime

  class Config:
    from_attributes = True