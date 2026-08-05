# JipMunSeo backend (FastAPI)

## Setup

Python is required but was not found on this machine (only the Microsoft
Store alias). Install Python 3.11+ first: https://www.python.org/downloads/
(check "Add python.exe to PATH" during install), then:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # fill in ANTHROPIC_API_KEY, DATABASE_URL, QDRANT_URL
```

## Run

```powershell
uvicorn app.main:app --reload --port 8000
```

Docs at http://localhost:8000/docs

## Test

```powershell
pytest
```

## Layout

See [../ARCHITECTURE.md](../ARCHITECTURE.md) for the layer design.
