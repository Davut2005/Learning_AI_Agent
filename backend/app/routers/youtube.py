import re
from urllib.parse import parse_qs, urlparse

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models import Document, DocumentChunk, User
from app.schemas.youtube import YouTubeIngestResponse
from app.services.document_processing_service import process_document


# Mount with prefix="/documents" in main.py → POST /documents/youtube
router = APIRouter(tags=["youtube"])

def _extract_youtube_video_id(url: str) -> str | None:
    """Extract video ID from YouTube URL. Returns None if invalid."""
    if not url or not url.strip():
        return None
    url = url.strip()
    # youtu.be/VIDEO_ID
    if "youtu.be/" in url:
        match = re.search(r"youtu\.be/([a-zA-Z0-9_-]{11})", url)
        return match.group(1) if match else None
    # youtube.com/watch?v=VIDEO_ID or youtube.com/v/VIDEO_ID
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


@router.post("/youtube", response_model=YouTubeIngestResponse)
def ingest_youtube_transcript(
    background_tasks: BackgroundTasks,
    youtube_url: str = Form(..., description="Full YouTube video URL"),
    user_id: int = Form(...),
    db: Session = Depends(get_session),
) -> YouTubeIngestResponse:
    """
    Ingest a YouTube video transcript. Fetches transcript via youtube-transcript-api,
    creates a Document with source=URL and one DocumentChunk containing the full transcript text.
    Returns the new document id.
    """
    video_id = _extract_youtube_video_id(youtube_url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    user = db.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        raise HTTPException(
            status_code=422,
            detail="No transcript available for this video (disabled or not found).",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch transcript: {e!s}",
        ) from e

    full_text = " ".join(item["text"] for item in transcript_list).strip()
    if not full_text:
        raise HTTPException(
            status_code=422,
            detail="Transcript is empty.",
        )

    title = f"YouTube: {video_id}"
    if len(title) > 512:
        title = title[:512]
    source = f"https://www.youtube.com/watch?v={video_id}"

    doc = Document(
        user_id=user_id,
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
    db.commit()

    background_tasks.add_task(process_document, doc.id)

    return YouTubeIngestResponse(document_id=doc.id)