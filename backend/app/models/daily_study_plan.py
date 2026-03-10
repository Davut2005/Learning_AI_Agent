from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DailyStudyPlan(SQLModel, table=True):
    """A single day's study plan within a LearningPath, grouping chunks into a session."""

    __tablename__ = "daily_study_plans"

    id: Optional[int] = Field(default=None, primary_key=True)
    learning_path_id: int = Field(foreign_key="learning_paths.id", index=True)
    day_number: int = Field(description="1-indexed day within the learning path")
    title: str = Field(max_length=512)
    description: Optional[str] = Field(default=None)
    chunk_ids: List[int] = Field(
        default_factory=list,
        sa_column=Column(JSONB, nullable=False, server_default="[]"),
        description="Ordered list of DocumentChunk IDs to study on this day",
    )
    estimated_minutes: int = Field(default=30)
    created_at: datetime = Field(default_factory=_utc_now)
