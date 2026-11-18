from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class Employee(Base):
    __tablename__ = "employee"
    employee_id: Mapped[str] = mapped_column(String, primary_key=True)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str | None] = mapped_column(String, unique=True)
    role: Mapped[str] = mapped_column(String, nullable=False)