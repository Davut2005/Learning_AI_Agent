"""
Vector storage using PostgreSQL pgvector on document_chunks.
Chunks are created first (content, chunk_index); this service updates their embedding column.
Embedding dimension 1536 matches OpenAI text-embedding-3-small (LangChain + OpenAI).
"""

from typing import Any, List

from sqlalchemy import text

from app.database import engine


def _embedding_to_pgvector(embedding: List[float]) -> str:
    """Convert Python list of floats to pgvector literal string."""
    return "[" + ",".join(str(f) for f in embedding) + "]"


def insert_chunk_embedding(
    chunk_id: str,
    document_id: str,
    text: str,
    embedding: List[float],
) -> None:
    """
    Update the existing document_chunks row with the embedding.
    Chunk row must already exist (created by chunking or YouTube ingest).
    """
    embedding_str = _embedding_to_pgvector(embedding)
    with engine.connect() as conn:
        conn.execute(
            text("""
                UPDATE document_chunks
                SET embedding = :embedding::vector
                WHERE id = :chunk_id
            """),
            {"chunk_id": chunk_id, "embedding": embedding_str},
        )
        conn.commit()


def search_similar_chunks(
    embedding: List[float],
    top_k: int,
) -> List[dict[str, Any]]:
    """
    Return the most similar stored chunks by L2 distance (<->).
    Uses document_chunks.content and document_chunks.embedding.
    """
    embedding_str = _embedding_to_pgvector(embedding)
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT id, document_id, content
                FROM document_chunks
                WHERE embedding IS NOT NULL
                ORDER BY embedding <-> :embedding::vector
                LIMIT :top_k
            """),
            {"embedding": embedding_str, "top_k": top_k},
        )
        rows = result.fetchall()
    return [
        {"id": str(row[0]), "document_id": str(row[1]), "text": row[2] or ""}
        for row in rows
    ]
