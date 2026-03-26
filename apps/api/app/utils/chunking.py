from typing import List, Dict


def chunk_text(text: str, chunk_size: int = 800, chunk_overlap: int = 100) -> List[Dict]:
    """
    Split text into overlapping character-based chunks.

    Rules:
    - chunk_size must be > 0
    - chunk_overlap must be >= 0 and < chunk_size
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be greater than or equal to 0")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    normalized = text.strip()
    if not normalized:
        return []

    chunks: List[Dict] = []
    step = chunk_size - chunk_overlap
    start = 0
    chunk_index = 0

    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        chunk_content = normalized[start:end]

        chunks.append(
            {
                "chunk_index": chunk_index,
                "content": chunk_content,
                "start_char": start,
                "end_char": end,
            }
        )

        if end == len(normalized):
            break

        start += step
        chunk_index += 1

    return chunks