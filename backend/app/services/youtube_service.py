"""
YouTube transcript fetching with optional cookie-based auth.

Render (and other cloud providers) have their IPs blocked by YouTube.
Passing a Netscape-format cookies.txt file from a logged-in YouTube session
bypasses the block by making requests appear authenticated.

Usage on Render:
  1. Export cookies from your browser while logged into YouTube
     (e.g. "Get cookies.txt LOCALLY" Chrome extension → export as Netscape format)
  2. Upload the file somewhere your backend can read it (e.g. store in the repo
     as `backend/youtube_cookies.txt` — add to .gitignore, or use a Render Secret File)
  3. Set the env var:  YOUTUBE_COOKIES_PATH=/opt/render/project/src/backend/youtube_cookies.txt
"""

import logging
from pathlib import Path

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled

from core.config import settings

logger = logging.getLogger(__name__)


def _get_api() -> YouTubeTranscriptApi:
    """Return a YouTubeTranscriptApi instance, with cookies if the path is configured."""
    cookies_path = getattr(settings, "YOUTUBE_COOKIES_PATH", None)
    if cookies_path and Path(cookies_path).is_file():
        logger.info("YouTube: using cookies from %s", cookies_path)
        return YouTubeTranscriptApi(cookies=cookies_path)
    return YouTubeTranscriptApi()


def fetch_transcript(video_id: str) -> str:
    """
    Fetch the full transcript text for a YouTube video ID.

    Raises:
        ValueError  – transcript disabled / not found
        RuntimeError – network/YouTube block or unexpected error
    """
    try:
        api = _get_api()
        transcript = api.fetch(video_id)
        raw = transcript.to_raw_data()
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        raise ValueError(
            "No transcript available for this video (disabled or not found)."
        ) from e
    except Exception as e:
        raise RuntimeError(
            f"Failed to fetch transcript — YouTube may be blocking this server's IP. "
            f"Set YOUTUBE_COOKIES_PATH to a Netscape cookies.txt from a logged-in session. "
            f"Original error: {e!s}"
        ) from e

    text = " ".join(item["text"] for item in raw).strip()
    if not text:
        raise ValueError("Transcript is empty.")
    return text
