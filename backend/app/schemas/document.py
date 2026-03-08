from datetime import datetime

from pydantic import BaseModel


class DocumentMetadata(BaseModel):
    """Document metadata returned from the API."""

    id: int
    user_id: int
    title: str
    source: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentUploadResponse(BaseModel):
    """Response after successful document upload."""

    message: str = "Document uploaded successfully"
    document: DocumentMetadata
