# Learning AI Agent

A full-stack app with a **FastAPI** backend and **React** (Vite) frontend.
An AI Agent for users to track their learning path and to help to memorize the skills.

## Agent 1 - Knowledge Extraction Agent
## Agent 2 - Quiz Generation Agent

## Stack

| Part     | Tech                |
|----------|---------------------|
| Backend  | FastAPI, Python, uv |
| Frontend | React 19, Vite, TypeScript |
| AI       | LangChain + OpenAI (LLM + embeddings) |

## Quick start

### Backend (FastAPI)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # macOS/Linux
pip install fastapi uvicorn uv
uv run main.py
```

API: **http://localhost:8000**

### Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

App: **http://localhost:5173**

## Project layout

```
Learning_AI_Agent/
├── backend/          # FastAPI API
│   └── main.py
├── frontend/         # React + Vite app
└── README.md
```

## Scripts

**Backend**

- `uv run main.py` — run API with hot reload (port 8000)

**Frontend**

- `npm run dev` — dev server
- `npm run build` — production build
- `npm run preview` — preview production build
- `npm run lint` — run ESLint

## Environment

- Copy `.env.example` to `.env` in `backend/` (and `frontend/` if needed) and set your variables.
- **Backend:** set `OPENAI_API_KEY` in `backend/.env` (required for LangChain + OpenAI). For auth, set `SECRET_KEY` (e.g. `openssl rand -hex 32`); default is a dev-only value.
- Never commit `.env` or other secrets; they are listed in `.gitignore`.

## Pipeline & database

- **Schema (SQLModel):** On startup the backend runs `init_db()`: it enables the **pgvector** extension, creates all tables (users, documents, document_chunks, concepts, questions, question_reviews), and adds the `document_chunks.embedding` column if missing. **Use an empty database** — run `uv run main.py` and all tables are created automatically. No migrations.
- **Auth:** Sign up and log in via the app (JWT). Upload, documents, quiz, and dashboard require authentication. If no users exist at first run, a default user (dev@local.app) is still created for quick dev testing.
- **After upload (file or YouTube):** background pipeline: chunk → embed (OpenAI) → store vectors → **Agent 1** (concept extraction) → **Agent 2** (quiz generation). Concepts and questions appear once processing finishes.
- **File types:** **.pdf**, **.docx**,  **.txt** and **.md** are used for text extraction;
- **Image types:** **.jpg**, **.jpeg**,  **.png** and **.webp** are used for text extraction;


## License

MIT
