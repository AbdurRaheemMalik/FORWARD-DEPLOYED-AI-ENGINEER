# Complaint Resolution Assistant

FDM Forward Deployed AI Engineer cohort project: an AI assistant for a bank's complaint-handling team, built over six sprints. The API follows **openapi contract v2.2.0**.

## Architecture

```
src/
├── config.py                      settings, read from .env
├── api/                           HTTP layer (FastAPI)
│   ├── main.py                    create_app(): wires routers and error handlers
│   ├── deps.py                    actor headers, service dependency
│   ├── schemas.py                 strict request/response models (contract v2.2.0)
│   ├── errors.py                  error envelope
│   └── routers/
│       ├── health.py              /health/live, /health/ready
│       ├── customers.py           T-001, T-002
│       └── complaints.py          T-003, T-008, T-009
├── services/
│   └── complaint_service.py       one transaction per operation, applies the rules
├── domain/                        business rules, no database code
│   ├── models.py                  statuses, transitions, approval threshold
│   └── errors.py                  domain errors with code and HTTP status
├── data/                          data access, no business rules
│   ├── database_manager.py        engine and transaction()
│   ├── customer_repository.py
│   ├── account_repository.py
│   ├── complaint_repository.py
│   ├── history_repository.py
│   └── service_request_repository.py
└── model/                         SQLAlchemy ORM tables
    ├── customer.py
    ├── account.py
    ├── employee.py
    ├── complaint.py
    ├── complaint_status_history.py
    └── service_request.py
```

Each layer only calls the one below it. `src/config.py` is the single place settings are read.

### API: [src/api/](src/api/)
| Route | Op | Roles |
|---|---|---|
| `GET /health/live`, `GET /health/ready` | — | none |
| `GET /customers/{customer_id}` | T-001 | Analyst, Supervisor |
| `GET /customers/{customer_id}/accounts` | T-002 | Analyst, Supervisor |
| `GET /complaints/{complaint_id}` | T-003 | Analyst, Supervisor |
| `PATCH /complaints/{complaint_id}/status` | T-008 | Analyst, Supervisor (per transition) |
| `POST /complaints/{complaint_id}/close` | T-009 | Supervisor |

- **Identity:** `X-Actor-Id` (`EMP000`), `X-Actor-Role`, `X-Actor-Type` (`human`/`agent`); missing or invalid → 401 ([deps.py](src/api/deps.py)).
- **Schemas** ([schemas.py](src/api/schemas.py)) are strict allow-lists: unknown request fields → 422, responses carry contract fields only.
- **Errors** ([errors.py](src/api/errors.py)) all use `{"error": {code, message, correlation_id, retryable}}`.

### Service: [src/services/complaint_service.py](src/services/complaint_service.py)
`get_customer`, `get_accounts`, `get_complaint`, `change_status`, `close`. Every write appends a history row and returns an `audit_event_id` (`H00006` → `AUD-000006`). Repositories and the clock are injectable, so tests run on fakes.

### Domain: [src/domain/](src/domain/)
| Transition | Roles |
|---|---|
| Open → In Review | Analyst, Supervisor |
| In Review → Escalated | Analyst, Supervisor |
| Escalated → In Review | Supervisor |
| Close (from In Review or Escalated) | Supervisor; compensation > CAD 1,000.00 needs approval |

| Error | HTTP |
|---|---|
| `NOT_FOUND` | 404 |
| `FORBIDDEN_ROLE` | 403 |
| `INVALID_TRANSITION`, `APPROVAL_REQUIRED` | 409 |
| `DEPENDENCY_UNAVAILABLE` (database down) | 503 |

### Data and model: [src/data/](src/data/), [src/model/](src/model/)
`DatabaseManager.transaction()` commits on success and rolls back on any error. Tables: `customer`, `account`, `employee`, `complaint`, `complaint_status_history` (append-only), `service_request`.

## Tests
- `tests/api/`: health checks and one smoke test per route, on in-memory fakes ([tests/fakes.py](tests/fakes.py)).
- `tests/test_repositories.py`: repositories against a temporary SQLite file.

## Known gaps
- The ORM models don't match the repositories yet (`date_closed`, history IDs, `changed_by_role`); two strict xfail tests track this.
- `docs/database/bank.db` is the Week 2 data, not the seeded contract data.
- `deps.py` is a stand-in for the course starter.
- Next (3.3.x): 422/405/500/504 in the error envelope, correlation IDs, atomic write tests.
