"""Learning path CRUD + document/YouTube source management endpoints."""

import re
import uuid
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.exc import OperationalError
from sqlmodel import Session, select

from app.database import get_session
from app.models import Document, DocumentChunk, User
from app.models.learning_path import LearningPath
from app.models.daily_study_plan import DailyStudyPlan
from app.routers.auth import get_current_user
from app.schemas.learning_path import (
    DailyStudyPlanOut,
    LearningPathCreate,
    LearningPathOut,
    LearningPathSummary,
)
from app.services.document_processing_service import process_document
from core.config import settings

router = APIRouter(prefix="/learning-paths", tags=["learning-paths"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


def _get_upload_root() -> Path:
    backend_root = Path(__file__).resolve().parent.parent.parent
    return (backend_root / settings.UPLOAD_DIR).resolve()


def _extract_youtube_video_id(url: str) -> str | None:
    if not url or not url.strip():
        return None
    url = url.strip()
    if "youtu.be/" in url:
        match = re.search(r"youtu\.be/([a-zA-Z0-9_-]{11})", url)
        return match.group(1) if match else None
    parsed = urlparse(url)
    if parsed.hostname and ("youtube.com" in parsed.hostname or "youtu.be" in parsed.hostname):
        if parsed.path == "/watch" and parsed.query:
            qs = parse_qs(parsed.query)
            v = qs.get("v")
            if v and len(v[0]) == 11:
                return v[0]
        if parsed.path.startswith("/v/"):
            match = re.search(r"/v/([a-zA-Z0-9_-]{11})", parsed.path)
            return match.group(1) if match else None
    return None


def _get_path_or_404(path_id: int, user_id: int, db: Session) -> LearningPath:
    path = db.get(LearningPath, path_id)
    if not path or path.user_id != user_id:
        raise HTTPException(status_code=404, detail="Learning path not found")
    return path


# ── CRUD ──────────────────────────────────────────────────────────────────────

@router.post("", response_model=LearningPathOut, status_code=201)
def create_learning_path(
    body: LearningPathCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> LearningPathOut:
    """Create a new learning path (no documents yet)."""
    path = LearningPath(
        user_id=current_user.id,
        title=body.title,
        description=body.description,
        hours_per_day=body.hours_per_day,
        status="ready",  # no docs yet → ready immediately
    )
    db.add(path)
    db.commit()
    db.refresh(path)
    return LearningPathOut(
        **path.model_dump(),
        daily_plans=[],
    )


@router.get("", response_model=list[LearningPathSummary])
def list_learning_paths(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> list[LearningPathSummary]:
    """List all learning paths for the current user."""
    try:
        paths = list(
            db.exec(
                select(LearningPath)
                .where(LearningPath.user_id == current_user.id)
                .order_by(LearningPath.created_at.desc())
            ).all()
        )
        result = []
        for p in paths:
            doc_count = db.exec(
                select(Document).where(Document.learning_path_id == p.id)
            ).all()
            result.append(
                LearningPathSummary(
                    **p.model_dump(),
                    document_count=len(doc_count),
                )
            )
        return result
    except OperationalError:
        return []


@router.get("/{path_id}", response_model=LearningPathOut)
def get_learning_path(
    path_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> LearningPathOut:
    """Get a learning path with its full daily roadmap."""
    path = _get_path_or_404(path_id, current_user.id, db)
    plans = list(
        db.exec(
            select(DailyStudyPlan)
            .where(DailyStudyPlan.learning_path_id == path_id)
            .order_by(DailyStudyPlan.day_number)
        ).all()
    )
    return LearningPathOut(
        **path.model_dump(),
        daily_plans=[DailyStudyPlanOut.model_validate(p) for p in plans],
    )


@router.delete("/{path_id}", status_code=204)
def delete_learning_path(
    path_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> None:
    """Delete a learning path and all its daily plans."""
    path = _get_path_or_404(path_id, current_user.id, db)

    # Delete daily plans
    plans = list(
        db.exec(select(DailyStudyPlan).where(DailyStudyPlan.learning_path_id == path_id)).all()
    )
    for plan in plans:
        db.delete(plan)

    db.delete(path)
    db.commit()


# ── SOURCES ───────────────────────────────────────────────────────────────────

@router.post("/{path_id}/documents", status_code=202)
def add_document_to_path(
    path_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(...),
    db: Session = Depends(get_session),
) -> dict:
    """Upload a file and attach it to a learning path. Processing starts in background."""
    path = _get_path_or_404(path_id, current_user.id, db)

    suffix = Path(file.filename or "file").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    upload_root = _get_upload_root()
    user_dir = upload_root / "documents" / str(current_user.id)
    user_dir.mkdir(parents=True, exist_ok=True)

    unique_name = f"{uuid.uuid4().hex}{suffix}"
    file_path = user_dir / unique_name
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
        learning_path_id=path_id,
        title=title,
        source=source_rel,
    )
    db.add(doc)

    # Mark path as processing while new doc is being added
    path.status = "processing"
    db.add(path)
    db.commit()
    db.refresh(doc)

    background_tasks.add_task(process_document, doc.id)

    return {"document_id": doc.id, "status": "processing"}


@router.post("/{path_id}/youtube", status_code=202)
def add_youtube_to_path(
    path_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    youtube_url: str = Form(...),
    db: Session = Depends(get_session),
) -> dict:
    """Add a YouTube video transcript to a learning path. Processing starts in background."""
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

    path = _get_path_or_404(path_id, current_user.id, db)

    video_id = _extract_youtube_video_id(youtube_url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    try:
        transcript = YouTubeTranscriptApi().fetch(video_id)
        raw = transcript.to_raw_data()
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        raise HTTPException(
            status_code=422,
            detail="No transcript available for this video (disabled or not found).",
        ) from e
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch transcript: {e!s}") from e

    full_text = " ".join(item["text"] for item in raw).strip()
    if not full_text:
        raise HTTPException(status_code=422, detail="Transcript is empty.")

    title = f"YouTube: {video_id}"
    source = f"https://www.youtube.com/watch?v={video_id}"

    doc = Document(
        user_id=current_user.id,
        learning_path_id=path_id,
        title=title,
        source=source,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    chunk = DocumentChunk(
        document_id=doc.id,
        content=full_text,
        chunk_index=0,
    )
    db.add(chunk)

    path.status = "processing"
    db.add(path)
    db.commit()

    background_tasks.add_task(process_document, doc.id)

    return {"document_id": doc.id, "status": "processing"}
