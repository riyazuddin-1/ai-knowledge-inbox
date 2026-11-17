from sqlalchemy.orm import Session

from shared.models.content import ContentStatus
from shared.repositories.content import update_status
from shared.repositories.embedding import create_embedding
from shared.memory import add_to_vector_store
from services.ai import AI

def chunk_text(
    text: str, chunk_size: int = 600, overlap: int = 100
) -> list[str]:
  """Splits raw text into clean, overlapping character chunks."""
  if not text:
    return []

  text = text.strip()
  chunks = []
  start = 0
  text_length = len(text)

  while start < text_length:
    end = start + chunk_size
    chunk = text[start:end]
    chunks.append(chunk.strip())
    start += chunk_size - overlap

  return [c for c in chunks if c]

def generate_embedding(text: str) -> list[float]:
    """Generates a vector embedding using Gemini's text-embedding-004 model."""
    cleaned_text = text.replace("\n", " ")

    response = AI.gemini.models.embed_content(
        model="gemini-embedding-001",
        contents=cleaned_text,
    )

    if not response.embeddings:
        raise ValueError("No embeddings returned by Gemini")

    embedding = response.embeddings[0]

    if embedding is None or embedding.values is None:
        raise ValueError("Embedding values are missing")

    return list(embedding.values)

def process_content_embedding(db: Session, content_id: int, raw_text: str):
  """Orchestrates the background pipeline:

  1. Sets status to PROCESSING
  2. Slices content into text chunks
  3. Generates Gemini vectors for each chunk
  4. Persists to SQLite via embedding repository
  5. Pushes directly to the in-memory vector store matrix
  6. Sets status to READY (or FAILED on error)
  """
  try:
    # 1. Update content status to processing
    update_status(db, content_id, ContentStatus.PROCESSING)

    # 2. Chunk text
    chunks = chunk_text(raw_text)
    if not chunks:
      update_status(db, content_id, ContentStatus.FAILED)
      return

    # 3. Process chunks sequentially
    for index, chunk_text_content in enumerate(chunks):
      # Generate vector using Gemini (768 dimensions)
      vector = generate_embedding(chunk_text_content)

      # 4. Save to SQLite database using your repository model fields
      db_embedding = create_embedding(
          db=db,
          content_id=content_id,
          order=index,
          text=chunk_text_content,
          vector=vector,
      )

      # 5. Instantly add to the shared in-memory vector store
      add_to_vector_store(
          embedding=vector,
          metadata={
              "embedding_id": db_embedding.id,
              "content_id": content_id,
              "text": chunk_text_content,
          },
      )

    # 6. Mark content successfully ready
    update_status(db, content_id, ContentStatus.READY)

  except Exception as e:
    update_status(db, content_id, ContentStatus.FAILED)
    print(f"Error processing content embedding for ID {content_id}: {e}")
    raise e
