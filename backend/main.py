
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

from app.database import init_db
from app.routers import auth, chunks, documents, questions, youtube
from app.routers import learning_paths


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables and ensure pgvector/embedding column on startup (SQLModel, no Alembic)."""
    init_db()
    yield


app = FastAPI(
    title="Learning AI Tracker & Quiz",
    description="Backend for document-based learning and quiz generation.",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ "https://learning-ai-agent-frontend.vercel.app" , "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Learning AI Tracker & Quiz API", "docs": "/docs"}


app.include_router(auth.router)
app.include_router(learning_paths.router)
app.include_router(documents.router)
app.include_router(youtube.router, prefix="/documents")
app.include_router(chunks.router, prefix="/documents")
app.include_router(questions.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.exception_handler(OperationalError)
def handle_db_unavailable(_request: Request, exc: OperationalError):
    return JSONResponse(
        status_code=503,
        content={
            "detail": "Database unavailable. Check DATABASE_URL and network (e.g. Supabase host reachable).",
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
