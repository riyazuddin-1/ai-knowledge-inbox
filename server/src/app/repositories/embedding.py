import json
from sqlalchemy.orm import Session
from app.models.embedding import Embedding

def create_embedding(
    db: Session,
    content_id: int,
    order: int,
    text: str,
    vector: list[float],
):
  embedding = Embedding(
      content_id=content_id,
      order=order,
      text=text,
      embedding=json.dumps(vector),
  )
  db.add(embedding)
  db.commit()
  db.refresh(embedding)
  return embedding

def get_embeddings_by_content_id(db: Session, content_id: int):
  return (
      db.query(Embedding)
      .filter(Embedding.content_id == content_id)
      .order_by(Embedding.order)
      .all()
  )

def get_all_embeddings(db: Session):
  """Fetched during FastAPI startup to hydrate the in-memory vector store."""
  return db.query(Embedding).all()
