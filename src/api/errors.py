"""Error responses (Exercise 3.2.1, extended in 3.2.2; 3.3.2 completes it).

Every error uses the contract body:
    {"error": {"code", "message", "correlation_id", "retryable"}}
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

from src.domain.errors import DomainError


class ApiError(Exception):
    """Raised by API dependencies (for example missing actor headers)."""

    def __init__(self, http_status, code, message):
        super().__init__(message)
        self.http_status, self.code, self.message = http_status, code, message


def error_response(request: Request, http_status, code, message, retryable=False, details=None):
    error = {"code": code, "message": message, "correlation_id": "", "retryable": retryable}
    if details is not None:
        error["details"] = details
    return JSONResponse(status_code=http_status, content={"error": error})


def install_error_handlers(app):
    @app.exception_handler(DomainError)
    async def domain_error(request: Request, exc: DomainError):
        return error_response(request, exc.http_status, exc.code, exc.message, exc.retryable,
                              details=exc.details)

    @app.exception_handler(ApiError)
    async def api_error(request: Request, exc: ApiError):
        return error_response(request, exc.http_status, exc.code, exc.message)

    @app.exception_handler(OperationalError)
    def database_unavailable(request: Request, exc: OperationalError):
        # SQLAlchemy wraps the driver's error (SQLite or psycopg) in OperationalError.
        return error_response(request, 503, "DEPENDENCY_UNAVAILABLE",
                              "Complaint database unavailable.", retryable=True)
