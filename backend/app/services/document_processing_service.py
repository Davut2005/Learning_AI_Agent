
import logging
from pathlib import Path

from sqlmodel import Session, select

from ..database import engine
from ..models import Concept, Document, DocumentChunk
from .chunking import chunk_and_store
from .concept_service import extract_concepts_from_chunk
from .embedding_service import create_embedding
from .question_service import generate_questions_for_concept
from .text_extraction import extract_text
from .vector_store import insert_chunk_embedding
from ..config import settings

logger = logging.getLogger(__name__)

_BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent


def _get_upload_root() -> Path:
    return (_BACKEND_ROOT / settings.UPLOAD_DIR).resolve()


def _read_document_text(source: str) -> str | None:
    """
    Extract text from an uploaded file (TXT, MD, PDF, DOCX).
    Returns None for YouTube/HTTP sources or if extraction fails.
    """
    if not source or source.startswith("http://") or source.startswith("https://"):
        return None

    upload_root = _get_upload_root()
    path = (upload_root / source).resolve()

    if not path.exists() or not path.is_file():
        logger.warning("Document processing: file not found at %s", path)
        return None

    try:
        text = extract_text(path)
        logger.info("Document processing: extracted %d chars from '%s'", len(text), path.name)
        return text
    except (ValueError, RuntimeError) as e:
        logger.warning("Document processing: extraction failed for '%s': %s", path.name, e)
        return None
    except Exception as e:
        logger.exception("Document processing: unexpected error reading '%s': %s", path.name, e)
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
                # Store vector (PostgreSQL pgvector)
                insert_chunk_embedding(
                    chunk_id=str(chunk_id),
                    document_id=doc_id_str,
                    content=content,
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

        # If this document belongs to a learning path, regenerate the roadmap
        with Session(engine) as db:
            doc = db.get(Document, document_id)
            learning_path_id = doc.learning_path_id if doc else None

        if learning_path_id:
            from app.services.roadmap_service import generate_roadmap
            generate_roadmap(learning_path_id)

    except Exception as e:
        logger.exception("Document processing failed for document_id=%s: %s", document_id, e)
