# ReconAI

ReconAI is a financial payment reconciliation system. This repository currently contains the **Phase 1 backend foundation** only: configuration, PostgreSQL connectivity, SQLAlchemy, Alembic, and a health endpoint.

Reconciliation matching, allocation, CSV intelligence, authentication, and the frontend are **not implemented yet**.

## Requirements

- Python 3.13
- PostgreSQL (for database connectivity checks and future migrations)

## Setup

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
copy .env.example .env
```

Edit `.env` and set `DATABASE_URL` to your local PostgreSQL connection string. Do not commit `.env`.

## Run the API

From the `backend` directory:

```powershell
cd backend
uvicorn app.main:app --reload
```

Health checks:

- `GET /health` — application liveness (`{"status": "ok"}`)
- `GET /health/db` — database connectivity (`200` when connected, `503` when unavailable)

OpenAPI docs are available at `/docs` while the server is running.

## Tests

```powershell
cd backend
pytest
```

Tests initialize the SQLAlchemy engine from `DATABASE_URL`. They do not require a live PostgreSQL instance except for `GET /health/db`.

## Migrations

Alembic is configured under `backend/app/db/migrations`. There are **no schema migrations yet**; domain models will be added in a later phase.

```powershell
cd backend
alembic current
```

## Configuration

| Variable | Purpose | Example |
| --- | --- | --- |
| `APP_NAME` | FastAPI application title | `ReconAI` |
| `DATABASE_URL` | SQLAlchemy PostgreSQL URL | `postgresql+psycopg://USER:PASSWORD@localhost:5432/reconai` |

Credentials must come from the environment. They are not stored in application code or `alembic.ini`.
