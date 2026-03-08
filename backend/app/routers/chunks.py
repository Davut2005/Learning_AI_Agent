"""Chunking endpoint: create DocumentChunk records from document text."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models import Document
from app.schemas.chunk import ChunkCreateRequest, ChunkCreateResponse, ChunkItem
from app.services.chunking import chunk_and_store

router = APIRouter(tags=["chunks"])


@router.post("/chunk", response_model=ChunkCreateResponse)
def create_chunks(
    body: ChunkCreateRequest,
    db: Session = Depends(get_session),
) -> ChunkCreateResponse:
    """
    Chunk document text into 500–800 token segments and store as DocumentChunk.
    Input: document_id, text. Output: list of chunks (id, document_id, content, chunk_index).
    """
    doc = db.exec(select(Document).where(Document.id == body.document_id)).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    created = chunk_and_store(db, body.document_id, body.text)
    return ChunkCreateResponse(
        document_id=body.document_id,
        chunks=[ChunkItem.model_validate(c) for c in created],
    )
