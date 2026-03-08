"""
Embedding service using Ollama embeddings (e.g. nomic-embed-text).
"""

import requests
from typing import List

OLLAMA_BASE_URL = "http://localhost:11434"
EMBED_URL = f"{OLLAMA_BASE_URL}/api/embed"
DEFAULT_MODEL = "nomic-embed-text"


def create_embedding(text: str, model: str = DEFAULT_MODEL) -> List[float]:
    """
    Send a POST request to Ollama /api/embed and return the embedding vector.
    Uses nomic-embed-text by default (ollama pull nomic-embed-text).
    """
    payload = {
        "model": model,
        "input": text,
    }
    resp = requests.post(EMBED_URL, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    # Response: {"embeddings": [[...]]} or {"embedding": [...]}
    emb = data.get("embeddings") or data.get("embedding")
    if not emb:
        return []
    # Single vector: emb is list of floats, or list of one vector
    return list(emb[0]) if emb and isinstance(emb[0], list) else list(emb)
