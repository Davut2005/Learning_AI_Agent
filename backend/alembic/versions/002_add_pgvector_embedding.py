"""Add pgvector extension and embedding column to document_chunks for OpenAI embeddings.

Revision ID: 002
Revises: 001
Create Date: 2025-03-08

Embedding dimension 1536 matches OpenAI text-embedding-3-small (LangChain + OpenAI).
"""
from typing import Sequence, Union

from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    op.execute("ALTER TABLE document_chunks ADD COLUMN embedding vector(1536);")


def downgrade() -> None:
    op.execute("ALTER TABLE document_chunks DROP COLUMN IF EXISTS embedding;")
