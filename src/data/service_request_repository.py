from sqlalchemy import select
from sqlalchemy.orm import Session
from src.model.service_request import ServiceRequest


class ServiceRequestRepository:
    def __init__(self, session: Session):
        self._session = session
    def get_for_complaint(self, complaint_id):
        """Only request_id, request_type, status, created_date; ordered by created_date, request_id."""
        stmt = (
            select(ServiceRequest.request_id, ServiceRequest.request_type,
                   ServiceRequest.status, ServiceRequest.created_date)
            .where(ServiceRequest.complaint_id == complaint_id)
            .order_by(ServiceRequest.created_date, ServiceRequest.request_id)
        )
        return [dict(row) for row in self._session.execute(stmt).mappings()]