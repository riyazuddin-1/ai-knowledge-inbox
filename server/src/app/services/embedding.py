from app.services.ai import AI
from app.core.tokenization import split_into_token_chunks


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 80) -> list[str]:
    """Split text into overlapping chunks measured with the configured tokenizer."""
    return split_into_token_chunks(text, chunk_size=chunk_size, overlap=overlap)

def generate_embedding(text: str) -> list[float]:
    return AI.embed_text(text)
