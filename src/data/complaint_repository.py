from sqlalchemy import select
from sqlalchemy.orm import Session
from src.model.complaint import Complaint


class ComplaintRepository:
    def __init__(self,session:Session):
        self._session=session
    def get_by_id(self,complaint_id):
        return self._session.get(Complaint,complaint_id)
    def get_for_customer(self,customer_id):
        s=(
            select(Complaint)
            .where(Complaint.customer_id==customer_id)
        )
        return list(self._session.scalars(s))
    def create(self,complaint):
        self._session.add(complaint)
        self._session.flush()
        return complaint