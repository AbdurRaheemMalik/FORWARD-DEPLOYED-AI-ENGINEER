from sqlalchemy.orm import Session
from sqlalchemy import select
from src.model.customer import Customer



class CustomerRepository:
    """Reads and saves customers. No business rules."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, customer_id: str) -> Customer | None:
        return self._session.get(Customer, customer_id)