"""Learning AI Tracker & Quiz — FastAPI app. Run with: uvicorn main:app --reload."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routers import chunks, documents, youtube


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Optional: create tables if they don't exist (dev). Prefer: alembic upgrade head."""
    # create_db_and_tables()  # Uncomment for dev without running migrations
    yield


app = FastAPI(
    title="Learning AI Tracker & Quiz",
    description="Backend for document-based learning and quiz generation.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
def read_root():
    return {"message": "Learning AI Tracker & Quiz API", "docs": "/docs"}


app.include_router(documents.router)
app.include_router(youtube.router, prefix="/documents")
app.include_router(chunks.router, prefix="/documents")


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
