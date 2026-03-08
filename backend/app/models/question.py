from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel, Relationship


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Question(SQLModel, table=True):
    """Quiz question tied to a concept."""

    __tablename__ = "questions"

    id: int | None = Field(default=None, primary_key=True)
    concept_id: int = Field(foreign_key="concepts.id", index=True)
    question_text: str = Field(sa_column=Column(Text(), nullable=False))
    question_type: str = Field(
        max_length=64,
        description="e.g. multiple_choice, true_false, short_answer",
    )
    options: dict | None = Field(default=None, sa_column=Column(JSONB))
    correct_answer: str = Field(sa_column=Column(Text(), nullable=False))
    created_at: datetime = Field(default_factory=_utc_now)

    concept: Concept | None = Relationship(back_populates="questions")
    reviews: list["QuestionReview"] = Relationship(back_populates="question")


class QuestionReview(SQLModel, table=True):
    """User's review/answer record for a question (tracking and feedback)."""

    __tablename__ = "question_reviews"

    id: int | None = Field(default=None, primary_key=True)
    question_id: int = Field(foreign_key="questions.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    was_correct: bool = Field()
    rating: int | None = Field(default=None, ge=1, le=5)
    reviewed_at: datetime = Field(default_factory=_utc_now)

    question: Question | None = Relationship(back_populates="reviews")
