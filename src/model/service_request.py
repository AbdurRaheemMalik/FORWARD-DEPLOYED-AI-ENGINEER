from datetime import date
from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class ServiceRequest(Base):
    __tablename__ = "service_request"
    request_id: Mapped[str] = mapped_column(String, primary_key=True)
    complaint_id: Mapped[str | None] = mapped_column(ForeignKey("complaint.complaint_id"))
    request_type: Mapped[str | None] = mapped_column(String)
    status: Mapped[str | None] = mapped_column(String)
    created_date: Mapped[date | None] = mapped_column(Date)
