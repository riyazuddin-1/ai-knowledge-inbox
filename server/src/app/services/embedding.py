from app.services.ai import AI

def chunk_text(text: str, chunk_size: int = 600, overlap: int = 100) -> list[str]:
    """Splits raw text into clean, overlapping character chunks."""
    if not text:
        return []
    text = text.strip()
    chunks, start, text_length = [], 0, len(text)
    while start < text_length:
        end = start + chunk_size
        chunks.append(text[start:end].strip())
        start += chunk_size - overlap
    return [c for c in chunks if c]

def generate_embedding(text: str) -> list[float]:
    return AI.embed_text(text)
