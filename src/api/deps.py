"""Actor headers and service dependency (Exercise 3.2.2).

STAND-IN: the brief says to copy Sprint 2/Starters/Week3/src/api/deps.py unchanged.
That starter was not available locally, so this file implements the same interface
(Actor, get_actor, get_service, document_actor_headers) from the brief and contract
v2.2.0. Replace it with the official starter when you have it.

get_actor reads the three headers as OPTIONAL so a missing one gives
401 UNAUTHENTICATED (our envelope), not FastAPI's 422.
"""
import re
from dataclasses import dataclass
from typing import Optional

from fastapi import Header, Request
from fastapi.openapi.utils import get_openapi

from src.api.errors import ApiError

ACTOR_ID = re.compile(r"^EMP[0-9]{3}$")
ROLES = ("Analyst", "Supervisor")
ACTOR_TYPES = ("human", "agent")

# How the contract documents the headers (components/parameters).
ACTOR_HEADER_SCHEMAS = {
    "X-Actor-Id": {"type": "string", "pattern": ACTOR_ID.pattern, "example": "EMP001"},
    "X-Actor-Role": {"type": "string", "enum": list(ROLES)},
    "X-Actor-Type": {"type": "string", "enum": list(ACTOR_TYPES)},
}


@dataclass(frozen=True)
class Actor:
    actor_id: str
    role: str
    actor_type: str


def _unauthenticated(header):
    return ApiError(401, "UNAUTHENTICATED", f"Missing or invalid {header} header.")


def get_actor(
    x_actor_id: Optional[str] = Header(None, alias="X-Actor-Id"),
    x_actor_role: Optional[str] = Header(None, alias="X-Actor-Role"),
    x_actor_type: Optional[str] = Header(None, alias="X-Actor-Type"),
) -> Actor:
    if not x_actor_id or not ACTOR_ID.match(x_actor_id):
        raise _unauthenticated("X-Actor-Id")
    if x_actor_role not in ROLES:
        raise _unauthenticated("X-Actor-Role")
    if x_actor_type not in ACTOR_TYPES:   # required, no default
        raise _unauthenticated("X-Actor-Type")
    return Actor(actor_id=x_actor_id, role=x_actor_role, actor_type=x_actor_type)


def get_service(request: Request):
    return request.app.state.service


def document_actor_headers(app):
    """Show the actor headers in /docs as the contract does: required, with pattern/enum."""

    def openapi():
        if app.openapi_schema:
            return app.openapi_schema
        schema = get_openapi(title=app.title, version=app.version, routes=app.routes)
        for path_item in schema.get("paths", {}).values():
            for operation in path_item.values():
                for param in operation.get("parameters", []):
                    if param.get("in") == "header" and param["name"] in ACTOR_HEADER_SCHEMAS:
                        param["required"] = True
                        param["schema"] = ACTOR_HEADER_SCHEMAS[param["name"]]
        app.openapi_schema = schema
        return schema

    app.openapi = openapi
