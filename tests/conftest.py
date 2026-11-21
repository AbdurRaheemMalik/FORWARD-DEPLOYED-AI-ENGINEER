"""Shared fixture for the repository tests: a fresh SQLite database per test,
with small isolated test data. Never touches docs/database/bank.db."""
from datetime import date, datetime

import pytest

from src.data.database_manager import DatabaseManager
from src.model import Account, Base, Complaint, Customer, Employee


@pytest.fixture
def db(tmp_path):
    # A file in pytest's temp folder: our DatabaseManager opens a new connection per
    # session, and an in-memory "sqlite://" database would be empty in each one.
    manager = DatabaseManager(f"sqlite:///{tmp_path / 'test.db'}")
    Base.metadata.create_all(manager.engine)
    with manager.transaction() as session:
        session.add_all([
            Employee(employee_id="E1", first_name="Ana", last_name="Lyst",
                     email="ana@test.com", role="Analyst"),
            Customer(customer_id="C1", first_name="Test", last_name="Customer",
                     email="c1@test.com", segment="Retail"),
        ])
        # The models declare no relationship(), so SQLAlchemy may not order the
        # INSERTs by foreign key: flush each parent level before its children.
        session.flush()
        session.add_all([
            Account(account_id="A1", customer_id="C1", account_number="111",
                    account_type="Savings", status="ACTIVE", current_balance=100,
                    opened_date=date(2024, 1, 1)),
        ])
        session.flush()   # parents first, so the complaints' foreign keys resolve
        session.add_all([
            Complaint(complaint_id="CMP1", customer_id="C1", account_id="A1",
                      channel="Web", category="Fee Dispute", complaint_text="Fee",
                      priority="High", status="OPEN",
                      received_at=datetime(2025, 1, 1, 9, 0), assigned_analyst_id="E1"),
            Complaint(complaint_id="CMP2", customer_id="C1", account_id=None,
                      channel="Phone", category="Service Delay", complaint_text="Slow",
                      priority="Low", status="OPEN",
                      received_at=datetime(2025, 1, 2, 9, 0), assigned_analyst_id="E1"),
        ])
    yield manager
    manager.engine.dispose()
