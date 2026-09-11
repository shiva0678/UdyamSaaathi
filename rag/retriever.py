from typing import Any
import re

from rag.embeddings import embed_texts
from rag.vector_store import load_vector_store

STOP_WORDS = {
    "a", "an", "and", "before", "do", "for", "i", "is", "me", "of",
    "should", "the", "to", "what", "where", "with",
}


def retrieve(query: str, top_k: int = 3) -> list[dict[str, Any]]:
    index, chunks = load_vector_store()
    if not chunks:
        return []
    scores, positions = index.search(embed_texts([query]), len(chunks))
    query_tokens = {
        token
        for token in re.findall(r"[a-z0-9]+", query.lower())
        if token not in STOP_WORDS
    }
    ranked = []
    for score, position in zip(scores[0], positions[0]):
        if position < 0:
            continue
        chunk = chunks[position]
        chunk_tokens = {
            token
            for token in re.findall(r"[a-z0-9]+", chunk["text"].lower())
            if token not in STOP_WORDS
        }
        overlap = len(query_tokens & chunk_tokens)
        ranked.append((overlap, float(score), chunk))
    ranked.sort(key=lambda item: (-item[0], -item[1]))
    return [
        {**chunk, "score": round(score, 4)}
        for _, score, chunk in ranked[:top_k]
    ]
