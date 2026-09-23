# WeatherGPT (SIH PS 26068)

An intelligent weather intelligence and conversational assistant built for SIH Problem Statement 26068.

## Stack Overview
- **Backend:** FastAPI (Python 3.11), SQLAlchemy (Async), Alembic, Pydantic v2
- **Database:** PostgreSQL 16 + PostGIS + pgvector
- **Frontend Dashboard:** React + Vite + Tailwind CSS
- **Mobile Client:** Flutter (Riverpod, WebSocket, HTTP)
- **Tooling:** Docker Compose, Adminer

---

## Project Structure
```text
weathergpt/
├── backend/          # FastAPI async backend service & Alembic migrations
│   ├── app/          # Core logic, API routes, database sessions
│   ├── alembic/      # Database migrations (PostGIS + pgvector setup)
│   ├── Dockerfile    # Python 3.11-slim container
│   ├── requirements.txt
│   └── .env.example
├── docker/           # Custom container definitions (PostgreSQL + PostGIS + pgvector)
├── mobile/           # Flutter mobile app structure
├── web/              # React + Vite + Tailwind CSS dashboard
└── docker-compose.yml# Multi-service stack definition
```

---

## Quickstart (Phase 0)

### 1. Configure Environment
Copy `.env.example` in `backend/` to `.env`:
```bash
cp backend/.env.example backend/.env
```

### 2. Run with Docker Compose
Ensure Docker Desktop is running, then execute:
```bash
docker compose up --build
```

### 3. Verify Health & Extensions
- **FastAPI Root Health:** [http://localhost:8000/health](http://localhost:8000/health)
  ```json
  {"status": "ok"}
  ```
- **Database & Extensions Health:** [http://localhost:8000/api/v1/health/db](http://localhost:8000/api/v1/health/db)
  ```json
  {
    "status": "ok",
    "database": "connected",
    "extensions": {
      "postgis": {"installed": true, "version": "3.4.2"},
      "pgvector": {"installed": true, "version": "0.7.0"}
    }
  }
  ```
- **Adminer Database UI:** [http://localhost:8080](http://localhost:8080)
  - System: `PostgreSQL`
  - Server: `db`
  - Username: `weathergpt`
  - Password: `weathergpt_secret`
  - Database: `weathergpt_db`
- **Interactive API Documentation:** [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
