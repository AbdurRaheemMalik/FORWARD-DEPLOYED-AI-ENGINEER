from sqlalchemy import select
from sqlalchemy.orm import Session
from src.model.account import Account


class AccountRepository:
    """Reads and saves accounts. No business rules."""
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_for_customer(self, customer_id: str) -> list[Account]:
        """Every account of one customer, ordered by account_id (may be empty)."""
        stmt = select(Account).where(Account.customer_id == customer_id).order_by(Account.account_id)
        return list(self._session.scalars(stmt))
