# backend/shared/vector_store.py
import json
import numpy as np
from sqlalchemy.orm import Session
from shared.repositories.embedding import get_all_embeddings

_vector_matrix = np.empty((0, 768))
_chunk_metadata = []


def init_vector_store(db: Session):
  """Hydrates RAM from SQLite on server startup."""
  global _vector_matrix, _chunk_metadata
  records = get_all_embeddings(db)

  vectors = []
  metadata = []

  for r in records:
    vectors.append(json.loads(r.embedding))
    metadata.append({
        "embedding_id": r.id,
        "content_id": r.content_id,
        "text": r.text,
        "source_title": (
            r.content.title if r.content else f"Item #{r.content_id}"
        ),
        "source_url": r.content.source if r.content else None,
    })

  _vector_matrix = np.array(vectors) if vectors else np.empty((0, 768))
  _chunk_metadata = metadata


def add_to_vector_store(embedding: list[float], metadata: dict):
  """Appends newly embedded chunk to RAM."""
  global _vector_matrix, _chunk_metadata
  vec = np.array(embedding)

  if _vector_matrix.size == 0:
    _vector_matrix = np.array([vec])
  else:
    _vector_matrix = np.vstack([_vector_matrix, vec])

  _chunk_metadata.append(metadata)


def search_vector_store(query_embedding: list[float], top_k: int = 4) -> list[dict]:
  """Returns top K matching chunk metadata dicts using cosine similarity."""
  if _vector_matrix.size == 0:
    return []

  query_vec = np.array(query_embedding)
  norms = np.linalg.norm(_vector_matrix, axis=1) * np.linalg.norm(query_vec)
  # Avoid division by zero
  norms = np.where(norms == 0, 1e-10, norms)

  similarities = np.dot(_vector_matrix, query_vec) / norms
  top_indices = np.argsort(similarities)[::-1][:top_k]

  results = []
  for idx in top_indices:
    item = _chunk_metadata[idx].copy()
    item["score"] = float(similarities[idx])
    results.append(item)

  return results
