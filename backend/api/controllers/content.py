from fastapi import BackgroundTasks, HTTPException
from shared.database.sql import SessionLocal
from sqlalchemy.orm import Session
from math import ceil

from shared.models.content import Content, ContentType
from shared.repositories.content import add_title, create

def ingest_content(
    db: Session,
    background_tasks: BackgroundTasks,
    content_type: ContentType,
    data: str,
):
    cleaned_data = data.strip()
    if not cleaned_data:
        raise HTTPException(status_code=400, detail="Content cannot be empty.")

    if content_type == ContentType.TEXT:
        record = create(db=db, type=ContentType.TEXT, data=cleaned_data, source=None)
        if record is None:
            raise HTTPException(status_code=500, detail="Failed to create content record")
        
        first_line = cleaned_data.split("\n")[0]
        snippet_title = (first_line[:50] + "...") if len(first_line) > 50 else first_line
        add_title(db, record.id, snippet_title)

        from workers.chunk_embed.handler import process_content_embedding
        background_tasks.add_task(process_content_embedding, db=SessionLocal(), content_id=record.id, raw_text=cleaned_data)
        return record

    elif content_type == ContentType.URL:
        if not cleaned_data.startswith(("http://", "https://")):
            raise HTTPException(status_code=400, detail="URL must start with http:// or https://")

        record = create(db=db, type=ContentType.URL, data=cleaned_data, source=cleaned_data)
        if record is None:
            raise HTTPException(status_code=500, detail="Failed to create content record")
        add_title(db, record.id, cleaned_data)

        from workers.url_parser.handler import parse_and_process_url
        background_tasks.add_task(parse_and_process_url, db=SessionLocal(), content_id=record.id, url=cleaned_data)
        return record

def list_contents(db: Session, page: int = 1, limit: int = 25):
    page = max(1, page)
    limit = max(1, min(100, limit)) # Cap max limit at 100 for safety
    offset = (page - 1) * limit

    total_items = db.query(Content).count()
    total_pages = ceil(total_items / limit) if total_items > 0 else 1

    items = (
        db.query(Content)
        .order_by(Content.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "items": items,
        "pagination": {
            "page": page,
            "limit": limit,
            "total_items": total_items,
            "total_pages": total_pages,
        }
    }
