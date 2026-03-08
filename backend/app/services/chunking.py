"""
Text chunking service: split document text into chunks of 500–800 tokens.
Uses tiktoken for token counts; prefers sentence boundaries when possible.
"""

import re

import tiktoken
from sqlmodel import Session

from app.models import DocumentChunk

# Token range per chunk
MIN_CHUNK_TOKENS = 500
MAX_CHUNK_TOKENS = 800
TARGET_CHUNK_TOKENS = 650

# Encoding for tokenization (OpenAI-style; works for general text)
def _get_encoding() -> tiktoken.Encoding:
    try:
        return tiktoken.get_encoding("cl100k_base")
    except Exception:
        return tiktoken.get_encoding("gpt2")


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences (simple: on . ! ? followed by space or end)."""
    if not text or not text.strip():
        return []
    # Split on sentence-ending punctuation when followed by space or end
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def chunk_text(text: str) -> list[str]:
    """
    Split document text into chunks of 500–800 tokens.
    Prefers breaking at sentence boundaries; falls back to token boundaries if needed.
    Returns list of chunk strings (no DB writes).
    """
    if not text or not text.strip():
        return []

    encoding = _get_encoding()
    sentences = _split_sentences(text)
    if not sentences:
        # No sentence boundaries: chunk by raw token count
        tokens = encoding.encode(text)
        return _chunk_by_tokens(encoding, tokens)

    chunks: list[str] = []
    current: list[str] = []
    current_tokens = 0

    for sent in sentences:
        sent_tokens = encoding.encode(sent)
        n = len(sent_tokens)
        if n > MAX_CHUNK_TOKENS:
            # Flush current chunk if any
            if current:
                chunks.append(" ".join(current))
                current = []
                current_tokens = 0
            # Split long sentence by token count
            for sub in _chunk_by_tokens(encoding, sent_tokens):
                chunks.append(sub)
            continue
        if current_tokens + n > MAX_CHUNK_TOKENS and current:
            chunks.append(" ".join(current))
            current = []
            current_tokens = 0
        current.append(sent)
        current_tokens += n
        if current_tokens >= MIN_CHUNK_TOKENS:
            chunks.append(" ".join(current))
            current = []
            current_tokens = 0

    if current:
        chunks.append(" ".join(current))

    return chunks


def _chunk_by_tokens(encoding: tiktoken.Encoding, tokens: list[int]) -> list[str]:
    """Split tokens into chunks of MIN–MAX size when no sentence boundaries available."""
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + MAX_CHUNK_TOKENS, len(tokens))
        # Prefer ending near TARGET to avoid tiny last chunk
        if start + MIN_CHUNK_TOKENS <= len(tokens) and start + TARGET_CHUNK_TOKENS < len(tokens):
            end = min(start + TARGET_CHUNK_TOKENS, len(tokens))
        chunk_tokens = tokens[start:end]
        chunks.append(encoding.decode(chunk_tokens))
        start = end
    return chunks


def chunk_and_store(db: Session, document_id: int, text: str) -> list[DocumentChunk]:
    """
    Chunk document text (500–800 tokens per chunk) and persist as DocumentChunk rows.
    Returns the created DocumentChunk instances (with id and chunk_index set).
    """
    chunks_text = chunk_text(text)
    created: list[DocumentChunk] = []
    for i, content in enumerate(chunks_text):
        chunk = DocumentChunk(
            document_id=document_id,
            content=content,
            chunk_index=i,
        )
        db.add(chunk)
        created.append(chunk)
    db.commit()
    for c in created:
        db.refresh(c)
    return created
