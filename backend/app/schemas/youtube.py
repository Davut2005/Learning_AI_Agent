from pydantic import BaseModel


class YouTubeIngestResponse(BaseModel):
    """Response after ingesting a YouTube transcript."""

    document_id: int