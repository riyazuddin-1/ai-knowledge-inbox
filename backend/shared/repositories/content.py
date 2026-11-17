from sqlalchemy.orm import Session
from shared.models.content import Content, ContentStatus, ContentType

def create(db: Session, type: ContentType, data: str, source: str | None = None) -> Content | None:
    content = Content(content=data, type=type, source=source)
    db.add(content)
    db.commit()
    db.refresh(content)
    return content

def list(db: Session, limit: int = 25, offset: int = 0):
    # TODO
    pass

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
