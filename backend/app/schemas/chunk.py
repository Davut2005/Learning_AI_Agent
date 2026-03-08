from pydantic import BaseModel


class ChunkCreateRequest(BaseModel):
    """Request body for creating chunks from document text."""

    document_id: int
    text: str


class ChunkItem(BaseModel):
    """One stored chunk (id, document_id, text, chunk_index)."""

    id: int
    document_id: int
    content: str
    chunk_index: int

    model_config = {"from_attributes": True}


class ChunkCreateResponse(BaseModel):
    """Response after chunking and storing document text."""

    document_id: int
    chunks: list[ChunkItem]
