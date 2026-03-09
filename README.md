# Learning AI Agent

A full-stack app with a **FastAPI** backend and **React** (Vite) frontend.
An AI Agent for users to track their learning path and to help to memorize the skills.

## Agent 1 - Knowledge Extraction Agent
## Agent 2 - Quiz Generation Agent

## Stack

| Part     | Tech              |
|----------|-------------------|
| Backend  | FastAPI, Python   |
| Frontend | React 19, Vite, TypeScript |
| AI       | LangChain + OpenAI (LLM + embeddings) |

## Quick start

### Backend (FastAPI)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # macOS/Linux
pip install fastapi uvicorn
python main.py
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

- `python main.py` — run API with hot reload (port 8000)

**Frontend**

- `npm run dev` — dev server
- `npm run build` — production build
- `npm run preview` — preview production build
- `npm run lint` — run ESLint

## Environment

- Copy `.env.example` to `.env` in `backend/` (and `frontend/` if needed) and set your variables.
- **Backend:** set `OPENAI_API_KEY` in `backend/.env` (required for LangChain + OpenAI LLM and embeddings).
- Never commit `.env` or other secrets; they are listed in `.gitignore`.

## Pipeline & database

- **Migrations:** run `alembic upgrade head` in `backend/` so the `document_chunks` table has the `embedding` column. PostgreSQL must have the **pgvector** extension (e.g. Supabase provides it).
- **After upload (file or YouTube):** the backend runs a background pipeline: chunk → embed (OpenAI) → store vectors → **Agent 1** (concept extraction) → **Agent 2** (quiz question generation). Concepts and questions appear in the DB and in the app once processing finishes.
- **File types:** only **.txt** and **.md** are currently used for text extraction; PDF/DOCX uploads are stored but not yet processed for concepts/questions.

## License

MIT
