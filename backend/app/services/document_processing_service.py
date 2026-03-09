"""
Document processing pipeline: after upload, run chunk → embedding → vector store → concept extraction → question generation.
Runs asynchronously via FastAPI BackgroundTasks.
"""

import logging
from pathlib import Path

from sqlmodel import Session, select

from app.database import engine
from app.models import Concept, Document, DocumentChunk
from app.services.chunking import chunk_and_store
from app.services.concept_service import extract_concepts_from_chunk
from app.services.embedding_service import create_embedding
from app.services.question_service import generate_questions_for_concept
from app.services.vector_store import insert_chunk_embedding
from core.config import settings

logger = logging.getLogger(__name__)

_BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent


def _get_upload_root() -> Path:
    return (_BACKEND_ROOT / settings.UPLOAD_DIR).resolve()


def _read_document_text(source: str) -> str | None:
    """
    Read document text from file for .txt and .md. Returns None for URLs or unsupported types.
    """
    if not source or source.startswith("http://") or source.startswith("https://"):
        return None
    upload_root = _get_upload_root()
    path = (upload_root / source).resolve()
    if not path.exists() or not path.is_file():
        logger.warning("Document processing: file not found %s", path)
        return None
    suffix = path.suffix.lower()
    if suffix not in (".txt", ".md"):
        # PDF/DOCX could be added here with optional libs
        logger.warning("Document processing: unsupported file type %s (only .txt, .md supported)", suffix)
        return None
    try:
        return path.read_text(encoding="utf-8", errors="replace").strip()
    except Exception as e:
        logger.warning("Document processing: failed to read file %s: %s", path, e)
        return None


def process_document(document_id: int) -> None:
    """
    Run the full pipeline for a document:
    document → chunk → embedding → store vector → concept extraction → question generation.
    Intended to be run in a background task (FastAPI BackgroundTasks).
    """
    logger.info("Document processing started for document_id=%s", document_id)
    try:
        with Session(engine) as db:
            doc = db.get(Document, document_id)
            if not doc:
                logger.warning("Document processing: document_id=%s not found", document_id)
                return
            doc_id = doc.id
            chunks = list(
                db.exec(
                    select(DocumentChunk).where(DocumentChunk.document_id == doc_id).order_by(DocumentChunk.chunk_index)
                ).all()
            )
            # If no chunks (e.g. file upload), read file and chunk
            if not chunks:
                text = _read_document_text(doc.source)
                if not text:
                    logger.warning("Document processing: no text for document_id=%s (source=%s)", doc_id, doc.source)
                    return
                chunks = chunk_and_store(db, doc_id, text)
                if not chunks:
                    logger.warning("Document processing: no chunks produced for document_id=%s", doc_id)
                    return
            # Collect id and content before session closes
            chunk_data = [(c.id, c.content) for c in chunks]

        doc_id_str = str(doc_id)
        for chunk_id, content in chunk_data:
            try:
                # Embedding
                embedding = create_embedding(content)
                # Store vector (Supabase pgvector)
                insert_chunk_embedding(
                    chunk_id=str(chunk_id),
                    document_id=doc_id_str,
                    text=content,
                    embedding=embedding,
                )
                # Concept extraction
                extract_concepts_from_chunk(doc_id_str, content)
            except Exception as e:
                logger.exception("Document processing: error processing chunk id=%s: %s", chunk_id, e)

        # Question generation for all concepts of this document
        with Session(engine) as db:
            concepts = list(
                db.exec(select(Concept).where(Concept.document_id == doc_id)).all()
            )
        for concept in concepts:
            try:
                generate_questions_for_concept(doc_id_str, concept.name)
            except Exception as e:
                logger.exception("Document processing: error generating questions for concept %s: %s", concept.name, e)

        logger.info("Document processing completed for document_id=%s", document_id)
    except Exception as e:
        logger.exception("Document processing failed for document_id=%s: %s", document_id, e)
