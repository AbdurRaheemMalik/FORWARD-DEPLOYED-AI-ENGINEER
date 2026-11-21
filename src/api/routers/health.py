"""Health checks (Exercise 3.2.1). No actor headers needed.

live  = the process is up (never touches the database).
ready = the process can do real work (the database answers SELECT 1)."""
from fastapi import APIRouter, Request
from sqlalchemy import text

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/live")
def live():
    return {"status": "ok"}


@router.get("/ready")
def ready(request: Request):
    # No try/except: a database error escapes to the handler in src/api/errors.py (503).
    with request.app.state.db.transaction() as session:
        session.execute(text("SELECT 1"))
    return {"status": "ready", "checks": {"complaint_db": "ok"}}
