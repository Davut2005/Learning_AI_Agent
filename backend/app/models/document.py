from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import Column, Text
from sqlalchemy.orm import relationship
from sqlmodel import Field, SQLModel, Relationship


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Document(SQLModel, table=True):
    """Uploaded document (e.g. PDF, text) used for learning and quiz generation."""

    __tablename__ = "documents"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    learning_path_id: int | None = Field(
        default=None,
        foreign_key="learning_paths.id",
        index=True,
        description="Optional learning path this document belongs to",
    )
    title: str = Field(max_length=512)
    source: str = Field(max_length=1024, description="File path or URL")
    created_at: datetime = Field(default_factory=_utc_now)
    updated_at: datetime = Field(default_factory=_utc_now)

    chunks: list["DocumentChunk"] = Relationship(
        sa_relationship=relationship("DocumentChunk", back_populates="document"),
    )


class DocumentChunk(SQLModel, table=True):
    """A chunk of text from a document (for embedding and concept extraction later)."""

    __tablename__ = "document_chunks"

    id: int | None = Field(default=None, primary_key=True)
    document_id: int = Field(foreign_key="documents.id", index=True)
    content: str = Field(sa_column=Column(Text(), nullable=False))
    chunk_index: int = Field(default=0, description="Order within the document")
    created_at: datetime = Field(default_factory=_utc_now)

    document: Document | None = Relationship(
        sa_relationship=relationship("Document", back_populates="chunks"),
    )
