import json
from threading import Lock

import numpy as np
from app.repositories.embedding import get_all_embeddings

# In-memory storage for vectors and their metadata
_VECTOR_INDEX = []
_METADATA_INDEX = []
_CHAT_HISTORY: list[dict[str, str]] = []
_CHAT_HISTORY_LOCK = Lock()
MAX_CHAT_HISTORY_MESSAGES = 40


def get_chat_history() -> list[dict[str, str]]:
    """Return a snapshot of recent chat messages held in process memory."""
    with _CHAT_HISTORY_LOCK:
        return _CHAT_HISTORY.copy()


def add_chat_turn(question: str, answer: str) -> None:
    """Keep only the latest complete question/answer turns in process memory."""
    with _CHAT_HISTORY_LOCK:
        _CHAT_HISTORY.extend(
            (
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer},
            )
        )
        if len(_CHAT_HISTORY) > MAX_CHAT_HISTORY_MESSAGES:
            del _CHAT_HISTORY[: len(_CHAT_HISTORY) - MAX_CHAT_HISTORY_MESSAGES]

def fetch_vector_data_into_memory(db):
    """Loads existing embeddings from SQLite into RAM on startup."""
    from app.models.embedding import Embedding
    global _VECTOR_INDEX, _METADATA_INDEX
    _VECTOR_INDEX = []
    _METADATA_INDEX = []
    
    embeddings = get_all_embeddings(db)
    for emb in embeddings:
        # Parse the embedding that comes as a JSON string
        vector_data = emb.embedding
        if isinstance(vector_data, str):
            vector_data = json.loads(vector_data)

        _VECTOR_INDEX.append(np.array(vector_data, dtype=np.float32))
        _METADATA_INDEX.append({
            "embedding_id": emb.id,
            "content_id": emb.content_id,
            "text": emb.text,
            "source_title": emb.content.title if emb.content else None,
            "source_url": emb.content.source if emb.content else None,
        })


def add_to_similarity_index(embedding: list[float], metadata: dict):
    """Instantly appends a new vector and metadata to RAM."""
    global _VECTOR_INDEX, _METADATA_INDEX
    _VECTOR_INDEX.append(np.array(embedding, dtype=np.float32))
    _METADATA_INDEX.append(metadata)

def search_similarity(query_vector: list[float], top_k: int = 4):
    """Performs cosine similarity search against the in-memory vectors."""
    if not _VECTOR_INDEX:
        return []

    q_vec = np.array(query_vector, dtype=np.float32)
    vectors = np.array(_VECTOR_INDEX)

    # Cosine similarity calculation
    dot_products = np.dot(vectors, q_vec)
    norms = np.linalg.norm(vectors, axis=1) * np.linalg.norm(q_vec)
    scores = dot_products / (norms + 1e-8)

    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for idx in top_indices:
        match = _METADATA_INDEX[idx].copy()
        match["score"] = float(scores[idx])
        results.append(match)

    return results
