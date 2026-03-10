from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class LearningPath(SQLModel, table=True):
    """A user-defined learning path that groups documents into a structured daily roadmap."""

    __tablename__ = "learning_paths"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=512)
    description: Optional[str] = Field(default=None)
    hours_per_day: float = Field(default=1.0, description="Desired study hours per day")
    total_days: Optional[int] = Field(default=None, description="Computed after roadmap generation")
    status: str = Field(
        default="processing",
        max_length=50,
        description="processing | ready | error",
    )
    created_at: datetime = Field(default_factory=_utc_now)
    updated_at: datetime = Field(default_factory=_utc_now)
