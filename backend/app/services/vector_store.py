"""
Vector storage service using Supabase PostgreSQL pgvector for document chunk embeddings.
Table: document_chunks (id uuid, document_id uuid, text text, embedding vector(768))
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
    Insert a new row into document_chunks with id, document_id, text, and embedding.
    Converts the Python embedding list to PostgreSQL pgvector format.
    """
    embedding_str = _embedding_to_pgvector(embedding)
    with engine.connect() as conn:
        conn.execute(
            text("""
                INSERT INTO document_chunks (id, document_id, text, embedding)
                VALUES (:id, :document_id, :text, :embedding::vector)
            """),
            {"id": chunk_id, "document_id": document_id, "text": text, "embedding": embedding_str},
        )
        conn.commit()


def search_similar_chunks(
    embedding: List[float],
    top_k: int,
) -> List[dict[str, Any]]:
    """
    Return the most similar stored chunks by L2 distance (<->).
    Runs: SELECT id, document_id, text FROM document_chunks
          ORDER BY embedding <-> :embedding::vector LIMIT :top_k
    """
    embedding_str = _embedding_to_pgvector(embedding)
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT id, document_id, text
                FROM document_chunks
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
