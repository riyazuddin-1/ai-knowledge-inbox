from sqlalchemy.orm import Session
from app.models.content import ContentType, ContentStatus
from app.repositories.content import add_title, create, update_status
from app.repositories.embedding import create_embedding
from app.core.similarity import add_to_similarity_index
from app.services.ai import AI

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

def process_embedding_logic(db: Session, content_id: int, raw_text: str):
    """Core domain logic for chunking, embedding, and vector storage."""
    update_status(db, content_id, ContentStatus.PROCESSING)

    # Chunk text
    chunks = [raw_text.strip()[i:i+600].strip() for i in range(0, len(raw_text.strip()), 500)]
    chunks = [c for c in chunks if c]
    
    if not chunks:
        update_status(db, content_id, ContentStatus.FAILED)
        return

    for index, chunk_text in enumerate(chunks):
        cleaned_text = chunk_text.replace("\n", " ")
        response = AI.gemini.models.embed_content(
            model="gemini-embedding-001",
            contents=cleaned_text,
        )
        vector = list(response.embeddings[0].values)

        db_embedding = create_embedding(
            db=db, content_id=content_id, order=index, text=chunk_text, vector=vector
        )
        add_to_similarity_index(
            embedding=vector,
            metadata={"embedding_id": db_embedding.id, "content_id": content_id, "text": chunk_text},
        )

    update_status(db, content_id, ContentStatus.READY)
