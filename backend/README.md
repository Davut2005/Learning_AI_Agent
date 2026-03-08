# 🚀 Backend API (FastAPI)

This is the core service for the application, built with **FastAPI** and managed by **uv** for high-performance dependency management.

---

## 🛠 Tech Stack

* **Language:** Python 3.12+
* **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
* **Package Manager:** [uv](https://github.com/astral-sh/uv)
* **Server:** [Uvicorn](https://www.uvicorn.org/) (Running on port `8000`)

---

## ⚡ Quick Start

### 1. Prerequisites
Ensure you have `uv` installed. If not, run:

**PowerShell (Windows):**
```powershell
powershell -c "irm [https://astral-sh.uv.install.sh](https://astral-sh.uv.install.sh) | iex"

```bash
curl -LsSf [https://astral-sh.uv.install.sh](https://astral-sh.uv.install.sh) | sh

📂 Project Structure

backend/
├── main.py              # Application entry point
├── app/                 # Logic, routes, and schemas
├── pyproject.toml       # Modern Python project config
└── uv.lock              # Locked dependencies