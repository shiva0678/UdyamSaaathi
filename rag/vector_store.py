import json
from pathlib import Path
from typing import Any

import faiss

from rag.embeddings import embed_texts
from rag.process_documents import build_chunks

ROOT = Path(__file__).resolve().parent
INDEX_PATH = ROOT / "index.faiss"
METADATA_PATH = ROOT / "index_metadata.json"
DOCUMENTS_DIR = ROOT / "documents"


def build_vector_store() -> tuple[faiss.Index, list[dict[str, Any]]]:
    chunks = build_chunks()
    index = faiss.IndexFlatIP(256)
    index.add(embed_texts([chunk["text"] for chunk in chunks]))
    faiss.write_index(index, str(INDEX_PATH))
    METADATA_PATH.write_text(json.dumps(chunks, indent=2), encoding="utf-8")
    return index, chunks


def load_vector_store() -> tuple[faiss.Index, list[dict[str, Any]]]:
    source_documents = list(DOCUMENTS_DIR.glob("*.json"))
    if (
        not INDEX_PATH.exists()
        or not METADATA_PATH.exists()
        or any(path.stat().st_mtime > INDEX_PATH.stat().st_mtime for path in source_documents)
    ):
        return build_vector_store()
    index = faiss.read_index(str(INDEX_PATH))
    chunks = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    return index, chunks


if __name__ == "__main__":
    index, chunks = build_vector_store()
    print(f"Stored {index.ntotal} chunks with {len(chunks)} metadata records")
