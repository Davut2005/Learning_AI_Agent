"""Database engine and session for SQLModel + PostgreSQL."""

from sqlmodel import Session, create_engine, SQLModel

from core.config import settings
from app.models import (  # noqa: F401 — register models with metadata
    User,
    Document,
    DocumentChunk,
    Concept,
    Question,
    QuestionReview,
)

# Sync engine for Alembic and standard request handling
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)


def get_session():
    """Dependency-friendly session generator."""
    with Session(engine) as session:
        yield session


def create_db_and_tables() -> None:
    """Create all tables. Prefer Alembic migrations in production."""
    SQLModel.metadata.create_all(engine)
