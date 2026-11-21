from sqlalchemy import select, update
from sqlalchemy.orm import Session
from src.model.complaint import Complaint


class ComplaintRepository:
    def __init__(self, session: Session):
        self._session = session
    def get_by_id(self, complaint_id):
        return self._session.get(Complaint, complaint_id)
    def get_for_customer(self, customer_id):
        stmt = (
            select(Complaint)
            .where(Complaint.customer_id == customer_id)
            .order_by(Complaint.received_at, Complaint.complaint_id)
        )
        return list(self._session.scalars(stmt))
    def create(self, complaint):
        self._session.add(complaint)
        self._session.flush()
        return complaint
    def update_status(self, complaint_id, status, date_closed=None):
        """Set status and date_closed (a date for Closed, None otherwise). Returns the row count."""
        stmt = (
            update(Complaint)
            .where(Complaint.complaint_id == complaint_id)
            .values(status=status, date_closed=date_closed)
        )
        return self._session.execute(stmt).rowcount