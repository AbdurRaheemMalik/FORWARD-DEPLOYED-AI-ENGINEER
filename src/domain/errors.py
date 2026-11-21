"""Domain errors (Exercise 3.1.2).

Each error carries the contract `code` and the `http_status` the API returns,
so 3.3.2 can turn any of them into the same error body:
    {"code": error.code, "message": error.message}
"""


class DomainError(Exception):
    code = "INTERNAL_ERROR"
    http_status = 500
    retryable = False   # contract: true only for DEPENDENCY_UNAVAILABLE and TIMEOUT

    def __init__(self, message: str, details=None):
        super().__init__(message)
        self.message = message
        self.details = details   # optional list of {"field", "issue"}


# ---------- 404: something does not exist ----------

class NotFound(DomainError):
    """Base for every 'not found' error, so callers can catch them all with one except."""
    code = "NOT_FOUND"
    http_status = 404


# Contract v2.2.0 has one code for every missing record: NOT_FOUND.
class CustomerNotFound(NotFound):
    pass


class ComplaintNotFound(NotFound):
    pass


# ---------- business-rule errors ----------

class ForbiddenRole(DomainError):
    """The transition exists, but this role may not make it."""
    code = "FORBIDDEN_ROLE"
    http_status = 403


class InvalidTransition(DomainError):
    """No such transition (e.g. Open -> Escalated, or anything out of Closed)."""
    code = "INVALID_TRANSITION"
    http_status = 409


class ApprovalRequired(DomainError):
    """Compensation is above CAD 1,000.00, so the close needs approval first."""
    code = "APPROVAL_REQUIRED"
    http_status = 409