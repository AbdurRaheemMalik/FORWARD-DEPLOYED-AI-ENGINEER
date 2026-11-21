"""T-003, T-008 and T-009 (Exercise 3.2.2). Routes only translate; the service decides."""
from fastapi import APIRouter, Depends, Path

from src.api.deps import Actor, get_actor, get_service
from src.api.schemas import (COMPLAINT_ID, CloseComplaintRequest, CloseComplaintResult, Complaint,
                             StatusUpdateRequest, StatusUpdateResult)

router = APIRouter(prefix="/complaints")

ComplaintId = Path(pattern=COMPLAINT_ID, examples=["CP00057"])


@router.get("/{complaint_id}", response_model=Complaint, operation_id="get_complaint",
            tags=["Read tools"])
def get_complaint(complaint_id: str = ComplaintId, actor: Actor = Depends(get_actor),
                  service=Depends(get_service)):
    return service.get_complaint(complaint_id)


@router.patch("/{complaint_id}/status", response_model=StatusUpdateResult,
              operation_id="update_complaint_status", tags=["Case actions"])
def update_complaint_status(body: StatusUpdateRequest, complaint_id: str = ComplaintId,
                            actor: Actor = Depends(get_actor), service=Depends(get_service)):
    return service.change_status(complaint_id, body.target_status, body.reason,
                                 role=actor.role, actor_id=actor.actor_id)


@router.post("/{complaint_id}/close", response_model=CloseComplaintResult,
             operation_id="close_complaint", tags=["Case actions"])
def close_complaint(body: CloseComplaintRequest, complaint_id: str = ComplaintId,
                    actor: Actor = Depends(get_actor), service=Depends(get_service)):
    return service.close(complaint_id, body.resolution.compensation_cad,
                         role=actor.role, actor_id=actor.actor_id)
