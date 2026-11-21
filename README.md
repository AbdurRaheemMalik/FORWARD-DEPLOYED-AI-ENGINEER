# FDM Forward Deployed AI Engineer – Complaint Resolution Assistant

## Purpose
Guided project for the FDM Forward Deployed AI Engineer cohort. Over six sprints we build an AI assistant for a bank's complaint-handling team, covering specification, data, API, RAG, agents, a portal, deployment and readiness.

This README summarises what exists so far (end of Sprint 2 / start of Sprint 3).

## Progress so far

| Step | What was done | Where |
|------|---------------|-------|
| Sprint 1 | Repository structure, `.gitignore`, `.env.example`, first README | repo root |
| 3.1.1 | SQLAlchemy ORM models and repositories over the Week 2 SQLite database | `src/model/`, `src/data/` |
| 3.1.2 | Domain rules (statuses, transitions, approval threshold) and domain errors | `src/domain/` |
| 3.1.x | `ComplaintService`: reads plus status changes and closing, with audit history | `src/services/` |
| 3.2.1 | FastAPI app, settings, health checks and the first error handler, with tests | `src/api/`, `src/config.py`, `tests/api/` |

## Folders
```
spec/      specifications and requirements
docs/      team docs; docs/database/bank.db is the local SQLite database (not committed)
data/      sample and test data (no sensitive data committed)
src/
  config.py          settings, read from .env / environment variables
  model/             SQLAlchemy ORM tables
  data/              database manager and repositories (data access only, no business rules)
  domain/            business rules and domain errors (no database code)
  services/          ComplaintService: applies the rules using the repositories
  api/               FastAPI app, routers and error responses
tests/     automated tests (pytest)
```

## Architecture
Requests flow through four layers, each depending only on the one below it:

```
api (FastAPI routers)  ->  services (ComplaintService)  ->  data (repositories)  ->  model (ORM) / bank.db
                                    |
                                    v
                         domain (rules + errors)
```

- **`DatabaseManager`** ([src/data/database_manager.py](src/data/database_manager.py)) creates the engine (SQLite, foreign keys on) and exposes `transaction()`, a context manager that commits on success and rolls back on any exception.
- **Repositories** take a session and only read/write rows: `CustomerRepository`, `AccountRepository`, `ComplaintRepository`, `HistoryRepository` (append-only, no update/delete) and `ServiceRequestRepository`.
- **`ComplaintService`** ([src/services/complaint_service.py](src/services/complaint_service.py)) opens one transaction per operation, checks the domain rules, then writes. Repositories and the clock (`today`) are injectable so the service can be tested with fakes.
- **`create_app(db=None, service=None)`** ([src/api/main.py](src/api/main.py)) builds the FastAPI app; tests pass their own db/service objects.

### Database tables (ORM models)
`customer`, `account`, `employee`, `complaint`, `complaint_status_history`, `service_request`.

## Domain rules
Defined in [src/domain/models.py](src/domain/models.py).

**Enums:** `ComplaintStatus` (Open, In Review, Pending Approval, Escalated, Closed), `Category` (6 values), `Priority` (Low/Medium/High), `Channel` (Phone/Email/Branch/Web), `Role` (Analyst/Supervisor).

**Status changes** (`change_status`):

| From | To | Allowed roles |
|------|----|---------------|
| Open | In Review | Analyst, Supervisor |
| In Review | Escalated | Analyst, Supervisor |
| Escalated | In Review | Supervisor only |

Anything else is `INVALID_TRANSITION`; a valid transition by the wrong role is `FORBIDDEN_ROLE`.

**Closing** (`close`): only a Supervisor, only from Open, In Review or Escalated, and compensation must be **at most CAD 1,000.00** – anything strictly above needs approval (`APPROVAL_REQUIRED`).

Every status change or close appends a row to `complaint_status_history`, and the response includes an `audit_event_id` (e.g. history `H00281` → `AUD-000281`).

## Errors
Domain errors ([src/domain/errors.py](src/domain/errors.py)) carry a contract code and HTTP status:

| Error | Code | HTTP |
|-------|------|------|
| `CustomerNotFound` | `CUSTOMER_NOT_FOUND` | 404 |
| `ComplaintNotFound` | `COMPLAINT_NOT_FOUND` | 404 |
| `ForbiddenRole` | `FORBIDDEN_ROLE` | 403 |
| `InvalidTransition` | `INVALID_TRANSITION` | 409 |
| `ApprovalRequired` | `APPROVAL_REQUIRED` | 409 |

All API errors use one body shape:
```json
{"error": {"code": "...", "message": "...", "correlation_id": "", "retryable": false}}
```
So far only database outages are mapped (SQLAlchemy `OperationalError` → 503 `DEPENDENCY_UNAVAILABLE`, `retryable: true`). Mapping the domain errors is planned for Exercise 3.3.2.

## API endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health/live` | Process is up. Never touches the database. → `{"status": "ok"}` |
| GET | `/health/ready` | Database answers `SELECT 1`. → `{"status": "ready", "checks": {"complaint_db": "ok"}}`, or 503 if the database is down |

## Configuration
[src/config.py](src/config.py) is the single place settings are read (from the root `.env` or real environment variables):

| Variable | Default |
|----------|---------|
| `DB_PATH` | `docs/database/bank.db` |
| `DB_HOST` | `127.0.0.1` |
| `DB_PORT` | `5432` |
| `DB_NAME` | `complaints_training` |
| `LOG_LEVEL` | `INFO` |

Copy `.env.example` to `.env` and fill in values locally. Never commit `.env`.

## Prerequisites
- Git installed and configured (`user.name`, `user.email`)
- Python 3.11+ (and Node.js LTS for the portal later)
- Packages: `fastapi`, `uvicorn`, `sqlalchemy`, `httpx` (for FastAPI's `TestClient`), `pytest`, and optionally `python-dotenv`

## Running locally
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install fastapi uvicorn sqlalchemy httpx pytest python-dotenv

# start the API (from the repo root)
uvicorn src.api.main:app --reload
# then open http://127.0.0.1:8000/health/live or /docs

# run the tests
python -m pytest -q
```

## Tests
- [tests/api/test_health.py](tests/api/test_health.py) – `/health/live` works with no database; `/health/ready` returns the 503 error body when the database is down while `/health/live` still answers.
- [tests/test_repositories.py](tests/test_repositories.py) – placeholder, still empty.

## Next exercise
3.3.x: add the complaint/customer endpoints and map the domain errors to the contract error body (3.3.2).
