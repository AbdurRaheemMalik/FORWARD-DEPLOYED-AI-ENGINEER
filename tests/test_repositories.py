"""Exercise 2.4.2 Step 3: valid, missing and failure cases for the repositories.

Ported from the course version to this project's API: DatabaseManager.transaction()
(not session_scope), get_for_customer (not list_by_customer), ComplaintRepository.create
(not add). Attributes are read inside the transaction, because sessions expire objects
on commit.
"""
from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from src.data.account_repository import AccountRepository
from src.data.complaint_repository import ComplaintRepository
from src.data.customer_repository import CustomerRepository
from src.data.history_repository import HistoryRepository
from src.model import Complaint


def new_complaint(complaint_id, customer_id="C1"):
    return Complaint(complaint_id=complaint_id, customer_id=customer_id, channel="Web",
                     category="Fee Dispute", complaint_text="x", status="OPEN",
                     received_at=datetime(2025, 1, 3))


# ---------- valid cases ----------

def test_get_customer_by_id(db):
    with db.transaction() as session:
        customer = CustomerRepository(session).get_by_id("C1")
        assert (customer.first_name, customer.last_name) == ("Test", "Customer")


def test_list_accounts_for_customer(db):
    with db.transaction() as session:
        accounts = AccountRepository(session).get_for_customer("C1")
        assert [a.account_id for a in accounts] == ["A1"]


def test_list_complaints_for_customer_in_date_order(db):
    with db.transaction() as session:
        complaints = ComplaintRepository(session).get_for_customer("C1")
        assert [c.complaint_id for c in complaints] == ["CMP1", "CMP2"]


def test_complaint_without_account_is_returned(db):
    with db.transaction() as session:
        assert ComplaintRepository(session).get_by_id("CMP2").account_id is None


def test_created_complaint_is_committed(db):
    with db.transaction() as session:
        ComplaintRepository(session).create(new_complaint("CMP3"))
    with db.transaction() as session:   # a new session sees the committed row
        assert ComplaintRepository(session).get_by_id("CMP3") is not None


# ---------- missing cases ----------

def test_missing_customer_returns_none(db):
    with db.transaction() as session:
        assert CustomerRepository(session).get_by_id("NOPE") is None


def test_missing_complaint_returns_none(db):
    with db.transaction() as session:
        assert ComplaintRepository(session).get_by_id("NOPE") is None


def test_missing_customer_has_no_accounts_or_complaints(db):
    with db.transaction() as session:
        assert AccountRepository(session).get_for_customer("NOPE") == []
        assert ComplaintRepository(session).get_for_customer("NOPE") == []


# ---------- failure cases ----------

def test_duplicate_primary_key_raises_and_rolls_back(db):
    with pytest.raises(IntegrityError):
        with db.transaction() as session:
            repo = ComplaintRepository(session)
            repo.create(new_complaint("CMP4"))
            repo.create(new_complaint("CMP1"))   # already exists
    with db.transaction() as session:   # CMP4 was rolled back with the failed transaction
        assert ComplaintRepository(session).get_by_id("CMP4") is None


def test_unknown_foreign_key_is_rejected(db):
    with pytest.raises(IntegrityError):
        with db.transaction() as session:
            ComplaintRepository(session).create(new_complaint("CMP9", customer_id="NO_SUCH_CUSTOMER"))


def test_session_is_closed_after_error(db, monkeypatch):
    opened = []
    real_factory = db._sessions

    def tracking_factory():
        session = real_factory()
        session.close_calls = 0
        real_close = session.close

        def close():
            session.close_calls += 1
            real_close()

        session.close = close
        opened.append(session)
        return session

    monkeypatch.setattr(db, "_sessions", tracking_factory)
    with pytest.raises(RuntimeError):
        with db.transaction():
            raise RuntimeError("something went wrong")
    assert opened[0].close_calls == 1
    assert not opened[0].in_transaction()


# ---------- known model mismatches (fail until the models match the seeded database) ----------

@pytest.mark.xfail(strict=True, reason="Complaint model has no date_closed column")
def test_update_status_sets_status(db):
    with db.transaction() as session:
        assert ComplaintRepository(session).update_status("CMP1", "In Review") == 1


@pytest.mark.xfail(strict=True, reason="History model has no changed_by_role and uses integer ids, "
                                       "but HistoryRepository expects 'H00001'-style ids")
def test_history_add_and_read_back(db):
    with db.transaction() as session:
        repo = HistoryRepository(session)
        history_id = repo.add("CMP1", "Open", "In Review", datetime(2025, 1, 4), "Analyst")
        assert history_id == "H00001"
        assert repo.get_for_complaint("CMP1")[0]["history_id"] == "H00001"
