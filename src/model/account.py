from datetime import date
from decimal import Decimal
from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class Account(Base):
    __tablename__ = "account"
    account_id: Mapped[str] = mapped_column(String, primary_key=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customer.customer_id"), nullable=False)
    account_number: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    account_type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    current_balance: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), default=0)
    opened_date: Mapped[date] = mapped_column(Date, nullable=False)
