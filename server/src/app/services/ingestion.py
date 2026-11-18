from sqlalchemy.orm import Session
from app.models.content import ContentType
from app.repositories.content import add_title, create

def create_inbox_item(db: Session, content_type: ContentType, data: str):
    """Business logic for creating a new inbox record and setting its initial title."""
    cleaned_data = data.strip()
    if not cleaned_data:
        raise ValueError("Content cannot be empty.")

    if content_type == ContentType.TEXT:
        record = create(db=db, type=ContentType.TEXT, data=cleaned_data, source=None)
        if not record:
            raise RuntimeError("Failed to create content record.")
        
        first_line = cleaned_data.split("\n")[0]
        snippet_title = (first_line[:50] + "...") if len(first_line) > 50 else first_line
        add_title(db, record.id, snippet_title)
        return record

    elif content_type == ContentType.URL:
        if not cleaned_data.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")

        record = create(db=db, type=ContentType.URL, data=cleaned_data, source=cleaned_data)
        if not record:
            raise RuntimeError("Failed to create content record.")
        add_title(db, record.id, cleaned_data)
        return record

    raise ValueError(f"Unsupported content type: {content_type}")
