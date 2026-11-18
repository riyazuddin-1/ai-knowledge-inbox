from functools import lru_cache

import tiktoken


@lru_cache(maxsize=1)
def get_encoding() -> tiktoken.Encoding:
    return tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    return len(get_encoding().encode(text, disallowed_special=()))


def split_into_token_chunks(
    text: str,
    chunk_size: int = 500,
    overlap: int = 80,
) -> list[str]:
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Chunk size must be positive and overlap must be smaller than chunk size.")

    text = text.strip()
    if not text:
        return []

    encoding = get_encoding()
    token_ids = encoding.encode(text, disallowed_special=())
    chunks = []
    start = 0

    while start < len(token_ids):
        end = min(start + chunk_size, len(token_ids))
        while end > start:
            try:
                chunk = encoding.decode(token_ids[start:end], errors="strict")
                break
            except UnicodeDecodeError:
                end -= 1
        else:
            end = min(start + 1, len(token_ids))
            while True:
                try:
                    chunk = encoding.decode(token_ids[start:end], errors="strict")
                    break
                except UnicodeDecodeError:
                    end += 1

        if chunk.strip():
            chunks.append(chunk.strip())
        if end >= len(token_ids):
            break

        next_start = max(start + 1, end - overlap)
        while next_start < end:
            try:
                encoding.decode(token_ids[next_start:end], errors="strict")
                break
            except UnicodeDecodeError:
                next_start += 1
        start = min(next_start, end)

    return chunks
