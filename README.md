# Learning AI Agent

A full-stack app with a **FastAPI** backend and **React** (Vite) frontend.
An AI Agent for users to track their learning path and to help to memorize the skills.

## Stack

| Part     | Tech              |
|----------|-------------------|
| Backend  | FastAPI, Python   |
| Frontend | React 19, Vite, TypeScript |

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
- Never commit `.env` or other secrets; they are listed in `.gitignore`.

## License

MIT
