# Learning AI Tracker & Quiz — Backend

FastAPI + PostgreSQL + SQLModel + Alembic. No AI logic yet; project structure and database only.

## Stack

- **Python 3.12+**
- **FastAPI**
- **PostgreSQL**
- **SQLModel** (ORM)
- **Alembic** (migrations)

## Setup

1. Create a PostgreSQL database, e.g. `learning_ai_tracker`.
2. Set `DATABASE_URL` in `.env` (see `core/config.py` for default).
3. Install deps (from `backend/`):

   ```bash
   uv sync
   ```

4. Run migrations:

   ```bash
   alembic upgrade head
   ```

5. Start the API:

   ```bash
   uvicorn main:app --reload
   ```

API: http://localhost:8000 — Docs: http://localhost:8000/docs

## Project layout

```
backend/
├── main.py              # FastAPI app, includes routers
├── alembic.ini
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── app/
│   ├── models/          # SQLModel table models (one file per domain)
│   │   ├── user.py
│   │   ├── document.py
│   │   ├── concept.py
│   │   └── question.py
│   ├── schemas/         # Pydantic request/response models (one file per domain)
│   │   ├── document.py
│   │   └── youtube.py
│   ├── routers/         # API route handlers (one file per resource/feature)
│   │   ├── documents.py # POST /documents/upload
│   │   └── youtube.py   # POST /documents/youtube
│   └── database.py
└── core/
    └── config.py
```

**Conventions:** Keep the project understandable by separating logic: one router file per feature (e.g. documents vs youtube), one schema file per domain, one model file per entity. Add new features in new router/schema files rather than overloading a single file.

## Models

| Model             | Purpose                                                |
|-------------------|--------------------------------------------------------|
| **User**          | Account (email, hashed_password, full_name)            |
| **Document**      | Uploaded doc per user (title, source)                 |
| **DocumentChunk** | Chunk of document text (for future embedding)          |
| **Concept**       | Learning concept per document                          |
| **Question**      | Quiz question per concept (type, options, correct_answer) |
| **QuestionReview**| User's answer/review per question (was_correct, rating) |

## Commands

- **New migration:** `alembic revision --autogenerate -m "description"`
- **Apply migrations:** `alembic upgrade head`
- **Rollback one:** `alembic downgrade -1`
