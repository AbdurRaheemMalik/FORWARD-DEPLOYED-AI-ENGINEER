"""Request and response models (Exercise 3.2.2). Field names, enums and patterns
follow openapi v2.2.0. Response models list ONLY contract fields, so nothing extra
(email, risk_category, balances) can leak even if a repository returns it."""
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from src.domain.models import Category, Channel, ComplaintStatus, Priority

CUSTOMER_ID = r"^C[0-9]{4}$"
ACCOUNT_ID = r"^A[0-9]{5}$"
COMPLAINT_ID = r"^CP[0-9]{5}$"
EVIDENCE_REF = (r"^(CP[0-9]{5}|C[0-9]{4}|A[0-9]{5}|(KB-[0-9]{3}|BUL-[0-9]{4}-[0-9]{2})#c[0-9]{3}"
                r"|NOTE-[0-9]{6}|APR-[0-9]{6})$")
HISTORY_ID = r"^H[0-9]{5}$"
SERVICE_REQUEST_ID = r"^SR[0-9]{5}$"
APPROVAL_ID = r"^APR-[0-9]{6}$"


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")   # unknown fields -> 422 VALIDATION_ERROR


class Customer(Strict):
    customer_id: str
    first_name: str
    last_name: str
    segment: str


class StatusUpdateRequest(Strict):
    target_status: ComplaintStatus
    reason: str = Field(min_length=5, max_length=500)


# ---------- T-002 ----------

class AccountSummary(Strict):
    """No balance, no account number."""
    account_id: str
    customer_id: str
    account_type: Literal["Chequing", "Savings", "Credit Card", "Mortgage"]
    status: Literal["Active", "Restricted", "Closed"]


class AccountList(Strict):
    customer_id: str
    accounts: List[AccountSummary]


# ---------- T-003 ----------

class StatusHistoryRow(Strict):
    """Contract schema ComplaintStatusHistory: one complaint_status_history row."""
    history_id: str = Field(pattern=HISTORY_ID)
    complaint_id: str = Field(pattern=COMPLAINT_ID)
    old_status: Optional[ComplaintStatus]          # required, null for the first row
    new_status: ComplaintStatus
    changed_at: date
    changed_by_role: Literal["System", "Analyst", "Supervisor"]


class ServiceRequest(Strict):
    request_id: str = Field(pattern=SERVICE_REQUEST_ID)
    request_type: Literal["Access Reset", "Document Request", "Fee Review",
                          "Manager Callback", "Transaction Investigation"]
    status: Literal["Open", "In Progress", "Completed"]
    created_date: date


class Complaint(Strict):
    complaint_id: str
    customer_id: str
    account_id: Optional[str] = None
    category: Category
    status: ComplaintStatus
    priority: Priority
    channel: Channel
    date_opened: date
    date_closed: Optional[date] = None
    summary: Optional[str] = None
    disputed_amount_cad: Optional[Decimal] = None
    history: List[StatusHistoryRow]
    linked_service_requests: List[ServiceRequest]


# ---------- T-008 ----------

class StatusUpdateResult(Strict):
    complaint_id: str
    previous_status: ComplaintStatus
    status: ComplaintStatus
    changed_by: str
    changed_at: datetime
    audit_event_id: str


# ---------- T-009 ----------

class Resolution(Strict):
    outcome: Literal["upheld", "partially_upheld", "not_upheld", "withdrawn"]
    summary: str = Field(min_length=10, max_length=2000)
    compensation_cad: Decimal = Field(default=Decimal("0"), ge=0)


class CloseComplaintRequest(Strict):
    resolution: Resolution
    communication_date: date
    evidence_refs: List[Annotated[str, Field(pattern=EVIDENCE_REF)]] = Field(min_length=1)
    approval_id: Optional[str] = Field(default=None, pattern=APPROVAL_ID)


class CloseComplaintResult(Strict):
    complaint_id: str
    previous_status: ComplaintStatus
    status: Literal["Closed"]
    date_closed: date
    closed_by: str
    approval_id: Optional[str] = None
    audit_event_id: str
