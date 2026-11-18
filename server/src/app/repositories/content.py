from math import ceil
from sqlalchemy.orm import Session
from app.models.content import Content, ContentStatus, ContentType

def create(db: Session, type: ContentType, data: str, source: str | None = None) -> Content | None:
    content = Content(content=data, type=type, source=source)
    db.add(content)
    db.commit()
    db.refresh(content)
    return content

def list_items(db: Session, page: int = 1, limit: int = 25):
    page = max(1, page)
    limit = max(1, min(100, limit))
    offset = (page - 1) * limit
    total_items = db.query(Content).count()
    total_pages = ceil(total_items / limit) if total_items > 0 else 1

    items = db.query(Content).order_by(Content.created_at.desc()).offset(offset).limit(limit).all()

    pagination_meta = {"page": page, "limit": limit, "total_items": total_items, "total_pages": total_pages}
    return items, pagination_meta

def get_by_id(db: Session, content_id: int):
    return db.query(Content).filter(Content.id == content_id).first()

def add_title(db: Session, content_id: int, title: str) -> Content | None:
    content = get_by_id(db, content_id)

    if not content:
        return None

    content.title = title
    db.commit()
    db.refresh(content)

    return content

def update_status(db: Session, content_id: int, status: ContentStatus):
    content = get_by_id(db, content_id)

    if not content:
        return None

    content.status = status
    db.commit()
    db.refresh(content)

    return content
