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
├── main.py              # FastAPI app
├── alembic.ini
├── alembic/
│   ├── env.py           # Alembic + SQLModel
│   ├── script.py.mako
│   └── versions/        # Migrations
├── app/
│   ├── models/          # SQLModel models
│   │   ├── user.py
│   │   ├── document.py
│   │   ├── concept.py
│   │   └── question.py
│   └── database.py      # Engine, session, create_db_and_tables
└── core/
    └── config.py        # Settings (DATABASE_URL, etc.)
```

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
