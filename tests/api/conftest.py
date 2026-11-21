"""Shared fixtures for the API tests (Exercise 3.2.2).

The real ComplaintService runs over the in-memory fakes from tests/fakes.py
(Exercise 3.1.2), so no database is needed.
"""
from datetime import date

import pytest
from fastapi.testclient import TestClient

from src.api.main import create_app
from src.services.complaint_service import ComplaintService
from tests.fakes import FakeDB, FakeStore, fake_repositories

ANALYST = {"X-Actor-Id": "EMP001", "X-Actor-Role": "Analyst", "X-Actor-Type": "human"}
SUPERVISOR = {"X-Actor-Id": "EMP002", "X-Actor-Role": "Supervisor", "X-Actor-Type": "human"}
TODAY = date(2026, 9, 1)


@pytest.fixture
def store():
    """A fresh sample store per test, with extra non-contract columns added as
    leak bait: they must never appear in a response."""
    s = FakeStore.sample()
    s.customers["C0096"].update(email="taylor@example.test", phone_number="555-0100")
    s.accounts["A00061"].update(account_number="000123456", current_balance="2510.33")
    return s


@pytest.fixture
def client(store):
    db = FakeDB(store)
    service = ComplaintService(db, fake_repositories(store), today=lambda: TODAY)
    return TestClient(create_app(db=db, service=service))
