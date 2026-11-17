from decimal import Decimal
from enum import Enum


class ComplaintStatus(str, Enum):
    OPEN = "Open"
    IN_REVIEW = "In Review"
    PENDING_APPROVAL = "Pending Approval"
    ESCALATED = "Escalated"
    CLOSED = "Closed"


class Category(str, Enum):
    FEES = "Fees"
    CARD_OR_TRANSACTION_DISPUTE = "Card or Transaction Dispute"
    DIGITAL_BANKING = "Digital Banking"
    SERVICE_QUALITY = "Service Quality"
    MORTGAGE_SERVICING = "Mortgage Servicing"
    ACCOUNT_ACCESS = "Account Access"


class Priority(str, Enum):
    # Called "urgency" by the 2.3.3 classifier; always "priority" in domain code.
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class Channel(str, Enum):
    # (contract): confirm these four spellings against openapi_contract.yaml
    # and complaints.csv. These are the values in our Week 2 bank.db.
    PHONE = "Phone"
    EMAIL = "Email"
    BRANCH = "Branch"
    WEB = "Web"


class Role(str, Enum):
    ANALYST = "Analyst"
    SUPERVISOR = "Supervisor"

S = ComplaintStatus

ALLOWED_TRANSITIONS: dict[tuple[ComplaintStatus, ComplaintStatus], frozenset[Role]] = {
    # TODO(contract): confirm the roles on the first two rows.
    (S.OPEN, S.IN_REVIEW): frozenset({Role.ANALYST, Role.SUPERVISOR}),
    (S.IN_REVIEW, S.ESCALATED): frozenset({Role.ANALYST, Role.SUPERVISOR}),
    # Confirmed by the exercise: only a Supervisor may de-escalate.
    (S.ESCALATED, S.IN_REVIEW): frozenset({Role.SUPERVISOR}),
}

# Statuses that POST /complaints/{id}/close accepts.
# TODO(contract): confirm against the /close description.
CLOSABLE: frozenset[ComplaintStatus] = frozenset({S.OPEN, S.IN_REVIEW, S.ESCALATED})

# Compensation strictly above this amount needs approval.
APPROVAL_THRESHOLD_CAD: Decimal = Decimal("1000.00")

INVALID_TRANSITION = "INVALID_TRANSITION"  # contract error code, HTTP 409
FORBIDDEN_ROLE = "FORBIDDEN_ROLE"          # contract error code, HTTP 403


# ---------------------------------------------------------------------------
# Helpers: they only look things up in the table above, so no status is
# hard-coded in a function body.
# ---------------------------------------------------------------------------

def can_transition(current, target, role) -> bool:
    """True if `role` may move a complaint from `current` to `target` via PATCH."""
    return transition_problem(current, target, role) is None


def transition_problem(current, target, role) -> str | None:
    """None if allowed, else the contract error code that explains why not:

    INVALID_TRANSITION (no such transition) or FORBIDDEN_ROLE (wrong role).
    Unknown status or role spellings raise ValueError.
    """
    key = (ComplaintStatus(current), ComplaintStatus(target))
    allowed_roles = ALLOWED_TRANSITIONS.get(key)
    if allowed_roles is None:
        return INVALID_TRANSITION
    if Role(role) not in allowed_roles:
        return FORBIDDEN_ROLE
    return None


def needs_approval(compensation_cad) -> bool:
    """True when the amount is above CAD 1,000.00 (strictly above)."""
    # str() first, so a float like 1000.0000001 is read exactly as written.
    return Decimal(str(compensation_cad)) > APPROVAL_THRESHOLD_CAD