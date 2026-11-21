from sqlalchemy import func, select
from sqlalchemy.orm import Session
from src.model.complaint_status_history import ComplaintStatusHistory as History


class HistoryRepository:
    """complaint_status_history is append-only: no update or delete methods."""
    def __init__(self, session: Session):
        self._session = session
    def get_for_complaint(self, complaint_id):
        """The six history columns, oldest first (changed_at, then history_id)."""
        stmt = (
            select(History.history_id, History.complaint_id, History.old_status,
                   History.new_status, History.changed_at, History.changed_by_role)
            .where(History.complaint_id == complaint_id)
            .order_by(History.changed_at, History.history_id)
        )
        return [dict(row) for row in self._session.execute(stmt).mappings()]
    def next_id(self):
        """'H' + (highest number + 1), five digits: H00281 after H00280."""
        highest = self._session.scalar(select(func.max(History.history_id)))
        number = int(highest[1:]) + 1 if highest else 1
        return f"H{number:05d}"
    def add(self, complaint_id, old_status, new_status, changed_at, changed_by_role):
        """Insert one row with next_id() and return its history_id."""
        history_id = self.next_id()
        self._session.add(History(history_id=history_id, complaint_id=complaint_id,
                                  old_status=old_status, new_status=new_status,
                                  changed_at=changed_at, changed_by_role=changed_by_role))
        self._session.flush()
        return history_id