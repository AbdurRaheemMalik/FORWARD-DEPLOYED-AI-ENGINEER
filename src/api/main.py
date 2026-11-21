"""
create_app() takes optional db and service objects so tests can pass their own.
"""
from fastapi import FastAPI

from src.data.database_manager import DatabaseManager
from src.api.deps import document_actor_headers
from src.api.errors import install_error_handlers
from src.api.routers import complaints, customers, health
from src.config import get_settings
from src.services.complaint_service import ComplaintService


def create_app(db=None, service=None):
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=settings.version)
    app.state.db = db or DatabaseManager()          # anything with transaction()
    app.state.service = service or ComplaintService(app.state.db)
    install_error_handlers(app)
    app.include_router(health.router)
    app.include_router(customers.router)
    app.include_router(complaints.router)
    document_actor_headers(app)
    return app


app = create_app()
