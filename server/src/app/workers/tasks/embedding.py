import logging

from app.core.database import SessionLocal
from app.models.content import ContentStatus
from app.repositories.content import update_status
from app.repositories.embedding import create_embedding
from app.core.memory import add_to_similarity_index
from app.services.embedding import chunk_text, generate_embedding

logger = logging.getLogger(__name__)


def run_embedding_task(content_id: int, raw_text: str):
    """Background task: manages DB session and delegates to services."""
    db = None
    embeddings = []
    try:
        db = SessionLocal()
        if update_status(db, content_id, ContentStatus.PROCESSING) is None:
            logger.error("Cannot embed content ID %s because it no longer exists.", content_id)
            return

        chunks = chunk_text(raw_text)
        if not chunks:
            update_status(db, content_id, ContentStatus.FAILED)
            logger.error("No text chunks were produced for content ID %s.", content_id)
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
            embeddings.append(
                (
                    vector,
                    {
                        "embedding_id": db_embedding.id,
                        "content_id": content_id,
                        "text": chunk_text_content,
                    },
                )
            )

        if update_status(db, content_id, ContentStatus.READY) is None:
            raise RuntimeError(f"Content ID {content_id} disappeared during embedding.")
        for vector, metadata in embeddings:
            add_to_similarity_index(embedding=vector, metadata=metadata)
    except Exception:
        logger.exception("Embedding task failed for content ID %s.", content_id)
        if db is not None:
            try:
                db.rollback()
                if update_status(db, content_id, ContentStatus.FAILED) is None:
                    logger.error("Could not mark missing content ID %s as failed.", content_id)
            except Exception:
                logger.exception("Could not mark content ID %s as failed.", content_id)
    finally:
        if db is not None:
            try:
                db.close()
            except Exception:
                logger.exception("Could not close the embedding DB session for content ID %s.", content_id)
