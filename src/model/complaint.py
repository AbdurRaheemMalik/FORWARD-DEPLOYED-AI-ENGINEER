from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class Complaint(Base):
    __tablename__ = "complaint"
    complaint_id: Mapped[str] = mapped_column(String, primary_key=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customer.customer_id"), nullable=False)
    account_id: Mapped[str | None] = mapped_column(ForeignKey("account.account_id"))
    channel: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    complaint_text: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str | None] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    assigned_analyst_id: Mapped[str | None] = mapped_column(ForeignKey("employee.employee_id"))