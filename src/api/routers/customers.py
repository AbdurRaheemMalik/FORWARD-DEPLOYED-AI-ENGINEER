"""T-001 and T-002 (Exercise 3.2.2)."""
from fastapi import APIRouter, Depends, Path

from src.api.deps import Actor, get_actor, get_service
from src.api.schemas import CUSTOMER_ID, AccountList, Customer

router = APIRouter(prefix="/customers", tags=["Read tools"])
CustomerId = Path(pattern=CUSTOMER_ID, examples=["C0096"])


@router.get("/{customer_id}", response_model=Customer, operation_id="get_customer")
def get_customer(customer_id: str = CustomerId, actor: Actor = Depends(get_actor),
                 service=Depends(get_service)):
    return service.get_customer(customer_id)


@router.get("/{customer_id}/accounts", response_model=AccountList, operation_id="get_accounts")
def get_accounts(customer_id: str = CustomerId, actor: Actor = Depends(get_actor),
                 service=Depends(get_service)):
    return service.get_accounts(customer_id)
