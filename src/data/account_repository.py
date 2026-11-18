from sqlalchemy import select
from sqlalchemy.orm import Session

from src.model.account import Account


class AccountRepository:
    """Reads and saves accounts. No business rules."""

    def __init__(self, session: Session) -> None:
        self._session = session
        
    def get_for_customer(self, account_id: str) -> Account | None:
        return self._session.get(Account, account_id)