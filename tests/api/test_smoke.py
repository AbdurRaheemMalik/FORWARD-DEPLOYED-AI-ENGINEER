"""Exercise 3.2.2: one smoke test per route, plus the no-prefix check. Uses the fakes in conftest.py."""
from tests.api.conftest import ANALYST, SUPERVISOR


def test_get_customer_returns_only_the_four_contract_fields(client):
    response = client.get("/customers/C0096", headers=ANALYST)
    assert response.status_code == 200
    assert set(response.json()) == {"customer_id", "first_name", "last_name", "segment"}


def test_get_accounts_has_no_balance(client):
    response = client.get("/customers/C0096/accounts", headers=ANALYST)
    assert response.status_code == 200
    body = response.json()
    assert body["customer_id"] == "C0096"
    assert len(body["accounts"]) == 1
    for account in body["accounts"]:
        assert set(account) == {"account_id", "customer_id", "account_type", "status"}


def test_get_complaint_with_history(client):
    response = client.get("/complaints/CP00002", headers=ANALYST)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "In Review"
    assert body["history"][0]["history_id"] == "H00002"
    assert body["history"][0]["old_status"] is None
    assert body["linked_service_requests"] == []


def test_patch_status_to_in_review_as_analyst(client):
    response = client.patch("/complaints/CP00001/status", headers=ANALYST,
                            json={"target_status": "In Review", "reason": "Starting the review."})
    assert response.status_code == 200
    body = response.json()
    assert body["previous_status"] == "Open"
    assert body["status"] == "In Review"
    assert body["changed_by"] == "EMP001"
    assert body["audit_event_id"] == "AUD-000006"


def test_close_as_supervisor(client):
    response = client.post("/complaints/CP00002/close", headers=SUPERVISOR, json={
        "resolution": {"outcome": "upheld", "summary": "Refunded the disputed card payment.",
                       "compensation_cad": 45.00},
        "communication_date": "2026-03-02",
        "evidence_refs": ["CP00002", "KB-003#c004"],
    })
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "Closed"
    assert body["previous_status"] == "In Review"
    assert body["closed_by"] == "EMP002"
    assert body["audit_event_id"] == "AUD-000006"


def test_no_api_v1_prefix(client):
    assert client.get("/api/v1/customers/C0096", headers=ANALYST).status_code == 404


# ---------- regression tests (beyond the six smoke tests) ----------

def test_get_complaint_after_patch_shows_the_new_history_row(client):
    patched = client.patch("/complaints/CP00001/status", headers=ANALYST,
                           json={"target_status": "In Review", "reason": "Starting the review."})
    assert patched.status_code == 200
    response = client.get("/complaints/CP00001", headers=ANALYST)
    assert response.status_code == 200
    last = response.json()["history"][-1]
    assert (last["old_status"], last["new_status"]) == ("Open", "In Review")
    assert last["changed_at"] == patched.json()["changed_at"][:10]   # date only


def test_open_complaint_cannot_be_closed(client):
    response = client.post("/complaints/CP00001/close", headers=SUPERVISOR, json={
        "resolution": {"outcome": "upheld", "summary": "Refunded the duplicate fee."},
        "communication_date": "2026-09-01",
        "evidence_refs": ["CP00001"],
    })
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "INVALID_TRANSITION"
