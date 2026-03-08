from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel, Relationship


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Concept(SQLModel, table=True):
    """Learning concept extracted from or associated with a document."""

    __tablename__ = "concepts"

    id: int | None = Field(default=None, primary_key=True)
    document_id: int = Field(foreign_key="documents.id", index=True)
    name: str = Field(max_length=255, index=True)
    description: str | None = Field(default=None, sa_column=Column(Text(), nullable=True))
    created_at: datetime = Field(default_factory=_utc_now)

    questions: list["Question"] = Relationship(back_populates="concept")
