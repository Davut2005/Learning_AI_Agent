"""Database engine and session for SQLModel + PostgreSQL. Tables created on startup (no Alembic)."""

import logging

from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlmodel import Session, create_engine, SQLModel, select

from core.config import settings
from app.models import (  # noqa: F401 — register models with metadata
    User,
    Document,
    DocumentChunk,
    Concept,
    Question,
    QuestionReview,
)

logger = logging.getLogger(__name__)

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)


def get_session():
    """Dependency-friendly session generator."""
    with Session(engine) as session:
        yield session


def init_db() -> None:
    """
    Create all tables and ensure pgvector + embedding column exist.
    Uses SQLModel only (no Alembic). Safe to run on an empty or existing database.
    If the database is unreachable (e.g. DNS), logs a warning and returns.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()

        # Create all tables: users, documents, document_chunks, concepts, questions, question_reviews
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created or already present.")

        with engine.connect() as conn:
            conn.execute(
                text("ALTER TABLE document_chunks ADD COLUMN IF NOT EXISTS embedding vector(1536)")
            )
            conn.commit()

        # Seed one default user (id=1) if no users exist — for dev until login/auth is implemented
        with Session(engine) as session:
            if session.exec(select(User.id)).first() is None:
                session.add(
                    User(
                        email="dev@local.app",
                        hashed_password="dev",
                        full_name="Dev User",
                    )
                )
                session.commit()
                logger.info("Default user created (email=dev@local.app, id=1). Add login/auth later.")
    except OperationalError as e:
        logger.warning(
            "Database unreachable at startup (e.g. DNS/network). "
            "App will start; list endpoints may return []; writes will return 503. Error: %s",
            e,
        )
