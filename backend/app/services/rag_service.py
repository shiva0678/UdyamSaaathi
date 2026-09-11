import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag.retriever import retrieve  # noqa: E402
from rag.vector_store import load_vector_store  # noqa: E402


def retrieve_context(query: str, top_k: int = 3) -> list[dict[str, Any]]:
    return retrieve(query, top_k=top_k)


def rag_available() -> bool:
    try:
        index, chunks = load_vector_store()
        return index.ntotal > 0 and bool(chunks)
    except Exception:
        return False
