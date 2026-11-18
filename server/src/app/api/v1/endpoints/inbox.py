import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import database
from app.schemas.inbox import IngestRequest, ContentResponse
from app.schemas.envelope import StandardResponse, PaginationMeta
from app.services.ingestion import create_inbox_item
from app.workers.tasks.embedding import run_embedding_task
from app.workers.tasks.url_parser import run_url_parser_task
from app.repositories.content import list_items
from app.models.content import ContentType

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Inbox & Ingestion"])

@router.post("/ingest", response_model=StandardResponse[ContentResponse], status_code=status.HTTP_202_ACCEPTED)
def ingest_item(
    payload: IngestRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(database),
):
    try:
        record = create_inbox_item(db=db, content_type=payload.type, data=payload.data)

        if payload.type == ContentType.TEXT:
            background_tasks.add_task(run_embedding_task, content_id=record.id, raw_text=record.content)
        elif payload.type == ContentType.URL:
            background_tasks.add_task(run_url_parser_task, content_id=record.id, url=payload.data)

        return StandardResponse(success=True, message="Content ingestion started successfully.", data=record)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as exc:
        logger.exception("Could not start content ingestion.")
        raise HTTPException(
            status_code=500,
            detail="Unable to start content ingestion right now.",
        ) from exc

@router.get("/items", response_model=StandardResponse[list[ContentResponse]], status_code=status.HTTP_200_OK)
def get_inbox_items(
    page: int = 1,
    limit: int = 25,
    db: Session = Depends(database),
):
    """Retrieves paginated inbox items with top-level pagination metadata."""
    try:
        items, pagination_meta = list_items(db=db, page=page, limit=limit)
        return StandardResponse(
            success=True,
            message="Items retrieved successfully.",
            data=items,
            pagination=PaginationMeta(**pagination_meta),
        )
    except Exception as exc:
        logger.exception("Could not retrieve inbox items.")
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve inbox items right now.",
        ) from exc
