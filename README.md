# JipMunSeo — 부동산 정책/세법 LLM Wiki Agent

부동산 정책과 세법을 위키처럼 찾아볼 수 있게 하는 LLM 에이전트. 법령/세법
근거와 실제 매매·임장 경험에서 나온 인사이트를 구분해서 제공하는 것이 핵심.

- `frontend/` — React + TypeScript (Vite)
- `backend/` — Python + FastAPI
- [ARCHITECTURE.md](ARCHITECTURE.md) — 레이어 설계 문서

## Quick start

```powershell
# frontend
cd frontend
npm run dev

# backend (Python 설치 필요, backend/README.md 참고)
cd backend
uvicorn app.main:app --reload --port 8000
```
