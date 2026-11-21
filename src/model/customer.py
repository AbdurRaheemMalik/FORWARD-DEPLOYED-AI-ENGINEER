from datetime import datetime
from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class Customer(Base):
    __tablename__ = "customer"
    customer_id: Mapped[str] = mapped_column(String, primary_key=True)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str | None] = mapped_column(String, unique=True)
    phone_number: Mapped[str | None] = mapped_column(String)
    segment: Mapped[str | None] = mapped_column(String)
    date_created: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )