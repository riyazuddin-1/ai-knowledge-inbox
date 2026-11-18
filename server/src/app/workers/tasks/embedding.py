from app.core.database import SessionLocal
from app.models.content import ContentStatus
from app.repositories.content import update_status
from app.repositories.embedding import create_embedding
from app.core.similarity import add_to_similarity_index
from app.services.embedding import chunk_text, generate_embedding

def run_embedding_task(content_id: int, raw_text: str):
    """Background task: manages DB session and delegates to services."""
    db = SessionLocal()
    try:
        update_status(db, content_id, ContentStatus.PROCESSING)

        chunks = chunk_text(raw_text)
        if not chunks:
            update_status(db, content_id, ContentStatus.FAILED)
            return

        for index, chunk_text_content in enumerate(chunks):
            vector = generate_embedding(chunk_text_content)
            db_embedding = create_embedding(
                db=db,
                content_id=content_id,
                order=index,
                text=chunk_text_content,
                vector=vector,
            )
            add_to_similarity_index(
                embedding=vector,
                metadata={
                    "embedding_id": db_embedding.id,
                    "content_id": content_id,
                    "text": chunk_text_content,
                },
            )

        update_status(db, content_id, ContentStatus.READY)
    except Exception as e:
        update_status(db, content_id, ContentStatus.FAILED)
        print(f"Error processing embedding for content ID {content_id}: {e}")
        raise e
    finally:
        db.close()
