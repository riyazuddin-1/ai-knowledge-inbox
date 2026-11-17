from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, BackgroundTasks, Depends, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.controllers.content import list_contents, ingest_content
from shared.database.sql import database
from shared.models.content import ContentStatus, ContentType
from shared.schemas.response import StandardResponse, PaginationMeta

router = APIRouter(tags=["Content"])

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


@router.post(
    "/ingest",
    response_model=StandardResponse[ContentResponse],
    status_code=status.HTTP_202_ACCEPTED,
)
def ingest_item(
    payload: IngestRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(database),
):
  record = ingest_content(
      db=db,
      background_tasks=background_tasks,
      content_type=payload.type,
      data=payload.data,
  )
  return StandardResponse(
      success=True,
      message="Content ingestion started successfully.",
      data=record
  )


@router.get("/items", response_model=StandardResponse[List[ContentResponse]])
def get_items(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(25, ge=1, le=100, description="Items per page"),
    db: Session = Depends(database)
):
  result = list_contents(db=db, page=page, limit=limit)
  return StandardResponse(
      success=True,
      message="Fetched items successfully.",
      data=result["items"],
      pagination=PaginationMeta(**result["pagination"])
  )
