from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
from src.data.account_repository import AccountRepository
from src.data.complaint_repository import ComplaintRepository
from src.data.customer_repository import CustomerRepository
from src.data.history_repository import HistoryRepository
from src.data.service_request_repository import ServiceRequestRepository
from src.domain.errors import ApprovalRequired, ComplaintNotFound, CustomerNotFound, ForbiddenRole, InvalidTransition
from src.domain.models import CLOSABLE, ComplaintStatus, Role, needs_approval, transition_problem


@dataclass
class Repositories:
    customers: object
    accounts: object
    complaints: object
    history: object
    requests: object

def make_repositories(conn):
    return Repositories(CustomerRepository(conn), AccountRepository(conn), ComplaintRepository(conn),
                        HistoryRepository(conn), ServiceRequestRepository(conn))

# Contract fields the service hands to the API. The API's Strict response models
# reject anything else (a 500, never a leak), so extra columns stop here.
CUSTOMER_FIELDS = ("customer_id", "first_name", "last_name", "segment")
ACCOUNT_FIELDS = ("account_id", "customer_id", "account_type", "status")
COMPLAINT_FIELDS = ("complaint_id", "customer_id", "account_id", "category", "status", "priority",
                    "channel", "date_opened", "date_closed", "summary", "disputed_amount_cad")


def _pick(row, fields):
    return {name: row[name] for name in fields if name in row}


def audit_event_id_for(history_id):
    return f"AUD-{int(history_id[1:]):06d}"

class ComplaintService:
    def __init__(self, db, repositories=make_repositories, today=date.today):
        self.db = db
        self.repositories = repositories
        self.today = today

    def get_customer(self, customer_id):
        with self.db.transaction() as conn:
            customer = self.repositories(conn).customers.get_by_id(customer_id)
            if customer is None:
                raise CustomerNotFound(f"Customer {customer_id} not found.")
            return _pick(_row(customer), CUSTOMER_FIELDS)

    def get_accounts(self, customer_id):
        with self.db.transaction() as conn:
            repos = self.repositories(conn)
            if repos.customers.get_by_id(customer_id) is None:
                raise CustomerNotFound(f"Customer {customer_id} not found.")
            accounts = [_pick(_row(a), ACCOUNT_FIELDS)
                        for a in repos.accounts.get_for_customer(customer_id)]
            return {"customer_id": customer_id, "accounts": accounts}

    def get_complaint(self, complaint_id):
        with self.db.transaction() as conn:
            repos = self.repositories(conn)
            complaint = repos.complaints.get_by_id(complaint_id)
            if complaint is None:
                raise ComplaintNotFound(f"Complaint {complaint_id} not found.")
            return self._complaint_with_children(repos, _pick(_row(complaint), COMPLAINT_FIELDS))

    def _complaint_with_children(self, repos, complaint):
        # Writes store changed_at as a datetime; the contract's history row has a date only.
        complaint["history"] = [{**row, "changed_at": _as_date(row["changed_at"])}
                                for row in repos.history.get_for_complaint(complaint["complaint_id"])]
        complaint["linked_service_requests"] = repos.requests.get_for_complaint(complaint["complaint_id"])
        return complaint

    def change_status(self, complaint_id, target_status, reason, role, actor_id=None):
        target, role = _v(target_status), _v(role)
        with self.db.transaction() as conn:
            repos = self.repositories(conn)
            complaint = repos.complaints.get_by_id(complaint_id)
            if complaint is None:
                raise ComplaintNotFound(f"Complaint {complaint_id} not found.")
            current = _row(complaint)["status"]

            problem = transition_problem(current, target, role)
            if problem == "INVALID_TRANSITION":
                ending = "; use close_complaint." if target == ComplaintStatus.CLOSED else "."
                raise InvalidTransition(f"Cannot move {complaint_id} from {current} to {target}{ending}")
            if problem == "FORBIDDEN_ROLE":
                raise ForbiddenRole(f"{role} cannot move {complaint_id} from {current} to {target}.")

            changed_at = datetime.now(timezone.utc)
            repos.complaints.update_status(complaint_id, target, date_closed=None)
            history_id = repos.history.add(complaint_id, current, target, changed_at, role)
            return {"complaint_id": complaint_id, "previous_status": current, "status": target,
                    "changed_by": actor_id, "changed_at": changed_at,
                    "audit_event_id": audit_event_id_for(history_id)}

    def close(self, complaint_id, compensation_cad=Decimal("0"), role="Supervisor", actor_id=None):
        role = _v(role)
        if role != Role.SUPERVISOR:
            raise ForbiddenRole(f"{role} cannot close a complaint.")
        with self.db.transaction() as conn:
            repos = self.repositories(conn)
            complaint = repos.complaints.get_by_id(complaint_id)
            if complaint is None:
                raise ComplaintNotFound(f"Complaint {complaint_id} not found.")
            current = _row(complaint)["status"]

            if ComplaintStatus(current) not in CLOSABLE:
                raise InvalidTransition(f"{complaint_id} cannot be closed from {current}.")
            if needs_approval(compensation_cad):
                raise ApprovalRequired(f"Compensation of CAD {compensation_cad} needs approval.")

            closed = ComplaintStatus.CLOSED.value
            date_closed = self.today()
            repos.complaints.update_status(complaint_id, closed, date_closed=date_closed)
            history_id = repos.history.add(complaint_id, current, closed, datetime.now(timezone.utc), role)
            return {"complaint_id": complaint_id, "previous_status": current, "status": closed,
                    "date_closed": date_closed, "closed_by": actor_id, "approval_id": None,
                    "audit_event_id": audit_event_id_for(history_id)}


def _as_date(value):
    """datetime -> date; a date (or None) is returned unchanged."""
    return value.date() if isinstance(value, datetime) else value


def _v(value):
    """Enum member or plain string -> plain string."""
    return getattr(value, "value", value)


def _row(record):
    """Dict (fakes) or SQLAlchemy model -> plain dict, read while the transaction is open."""
    if isinstance(record, dict):
        return dict(record)
    return {c.name: getattr(record, c.name) for c in record.__table__.columns}