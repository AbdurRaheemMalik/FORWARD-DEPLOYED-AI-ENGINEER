from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class ComplaintStatusHistory(Base):
    __tablename__ = "complaint_status_history"
    history_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    complaint_id: Mapped[str] = mapped_column(ForeignKey("complaint.complaint_id"), nullable=False)
    old_status: Mapped[str | None] = mapped_column(String)
    new_status: Mapped[str] = mapped_column(String, nullable=False)
    changed_by: Mapped[str | None] = mapped_column(ForeignKey("employee.employee_id"))
    changed_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.current_timestamp())
    comments: Mapped[str | None] = mapped_column(Text)