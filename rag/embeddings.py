import hashlib
import re
from typing import Iterable

import numpy as np

EMBEDDING_DIMENSION = 256


def _tokens(text: str) -> Iterable[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def embed_text(text: str) -> np.ndarray:
    vector = np.zeros(EMBEDDING_DIMENSION, dtype="float32")
    for token in _tokens(text):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "little") % EMBEDDING_DIMENSION
        vector[index] += 1.0
    norm = np.linalg.norm(vector)
    if norm:
        vector /= norm
    return vector


def embed_texts(texts: list[str]) -> np.ndarray:
    if not texts:
        return np.empty((0, EMBEDDING_DIMENSION), dtype="float32")
    return np.vstack([embed_text(text) for text in texts]).astype("float32")
