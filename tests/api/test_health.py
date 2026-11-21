"""Exercise 3.2.1: the two health checks, with no real database."""
from contextlib import contextmanager

from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from src.api.main import create_app


class BrokenDB:
    """A database that is always down: transaction() raises like a real outage."""

    @contextmanager
    def transaction(self):
        raise OperationalError("SELECT 1", {}, Exception("database down"))
        yield


def test_live_answers_without_a_database():
    client = TestClient(create_app(db=object(), service=object()))
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_is_503_when_database_is_down_but_live_still_answers():
    client = TestClient(create_app(db=BrokenDB(), service=object()), raise_server_exceptions=False)

    response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json() == {"error": {"code": "DEPENDENCY_UNAVAILABLE",
                                         "message": "Complaint database unavailable.",
                                         "correlation_id": "", "retryable": True}}

    assert client.get("/health/live").status_code == 200
