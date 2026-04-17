"""Document upload and management endpoints."""

import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.exc import OperationalError
from sqlmodel import Session, select

from ..database import get_session
from ..models import Document, User
from ..schemas.document import DocumentMetadata, DocumentUploadResponse
from ..services.document_processing_service import process_document
from ..routers.auth import get_current_user
from ..config import settings

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/markdown",
    "image/jpeg",
    "image/png",
    "image/webp",
}


def _get_upload_root() -> Path:
    """Absolute path to the upload base directory (backend/storage by default)."""
    backend_root = Path(__file__).resolve().parent.parent.parent
    return (backend_root / settings.UPLOAD_DIR).resolve()


def _validate_file(filename: str, content_type: str | None) -> None:
    """Raise HTTPException if file type is not allowed."""
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )
    if content_type and content_type not in ALLOWED_CONTENT_TYPES:
        # Be lenient: some clients send wrong content-type; extension is the source of truth
        pass


@router.get("", response_model=list[DocumentMetadata])
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> list[DocumentMetadata]:
    """List documents for the current user. Returns [] when database is unavailable."""
    try:
        docs = db.exec(select(Document).where(Document.user_id == current_user.id).order_by(Document.created_at.desc())).all()
        return [DocumentMetadata.model_validate(d) for d in docs]
    except OperationalError:
        return []


@router.post("/upload", response_model=DocumentUploadResponse)
def upload_document(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(...),
    db: Session = Depends(get_session),
) -> DocumentUploadResponse:
    """
    Upload a document (PDF, DOCX, TXT, or Markdown).
    File is saved locally and a Document record is created.
    """
    _validate_file(file.filename or "", file.content_type)

    upload_root = _get_upload_root()
    user_dir = upload_root / "documents" / str(current_user.id)
    user_dir.mkdir(parents=True, exist_ok=True)

    suffix = Path(file.filename or "file").suffix.lower()
    unique_name = f"{uuid.uuid4().hex}{suffix}"
    file_path = user_dir / unique_name
    # Relative path for DB (portable): documents/{user_id}/{unique_name}
    source_rel = f"documents/{current_user.id}/{unique_name}"

    try:
        contents = file.file.read()
    finally:
        file.file.close()

    file_path.write_bytes(contents)

    title = file.filename or unique_name
    if len(title) > 512:
        title = title[:509] + "..."

    doc = Document(
        user_id=current_user.id,
        title=title,
        source=source_rel,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    background_tasks.add_task(process_document, doc.id)

    return DocumentUploadResponse(
        document=DocumentMetadata.model_validate(doc),
    )
