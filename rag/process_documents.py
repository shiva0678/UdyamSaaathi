import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DOCUMENTS_DIR = ROOT / "documents"


def load_documents() -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    for path in sorted(DOCUMENTS_DIR.glob("*.json")):
        documents.extend(json.loads(path.read_text(encoding="utf-8")))
    return documents


def chunk_text(text: str, chunk_size: int = 80, overlap: int = 15) -> list[str]:
    words = text.split()
    if not words:
        return []
    step = max(1, chunk_size - overlap)
    return [" ".join(words[start : start + chunk_size]) for start in range(0, len(words), step)]


def build_chunks() -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    for document in load_documents():
        for index, text in enumerate(chunk_text(document["text"])):
            chunks.append(
                {
                    "document_name": document["document_name"],
                    "source": document["source"],
                    "text": text,
                    "metadata": {**document.get("metadata", {}), "chunk_index": index},
                }
            )
    return chunks
