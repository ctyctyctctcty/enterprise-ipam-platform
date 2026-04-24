from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.intake import (
    IntakeEvaluationRead,
    IntakeRequestRead,
    IntakeRequestStatusRead,
    IntakeRequestSubmit,
    IntakeTransitionRequest,
)
from app.services.intake import IntakeService

router = APIRouter()


@router.get("/", response_model=list[IntakeRequestRead])
def list_requests(db: Session = Depends(get_db)) -> list[IntakeRequestRead]:
    return IntakeService(db).list_requests()


@router.post("/submit", response_model=IntakeRequestRead)
def submit_request(payload: IntakeRequestSubmit, db: Session = Depends(get_db)) -> IntakeRequestRead:
    return IntakeService(db).create_request(payload)


@router.get("/status/{request_number}", response_model=IntakeRequestStatusRead)
def get_request_status(request_number: str, db: Session = Depends(get_db)) -> IntakeRequestStatusRead:
    request = IntakeService(db).get_by_request_number(request_number)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return IntakeRequestStatusRead(
        request_number=request.request_number,
        status=request.status,
        current_approval_order=request.current_approval_order,
        assigned_ip_address_id=request.assigned_ip_address_id,
        recommended_ip_address_id=request.recommended_ip_address_id,
        eligibility_outcome=request.eligibility_outcome,
        eligibility_summary=request.eligibility_summary,
    )


@router.post("/{request_id}/evaluate", response_model=IntakeEvaluationRead)
def evaluate_request(request_id: str, db: Session = Depends(get_db)) -> IntakeEvaluationRead:
    result = IntakeService(db).evaluate_request(request_id)
    if not result:
        raise HTTPException(status_code=404, detail="Request not found")
    return result


@router.post("/{request_id}/transition", response_model=IntakeRequestRead)
def transition_request(
    request_id: str,
    payload: IntakeTransitionRequest,
    db: Session = Depends(get_db),
) -> IntakeRequestRead:
    request = IntakeService(db).transition_request(
        request_id,
        payload.target_status,
        payload.comment,
    )
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return request


@router.get("/{request_id}", response_model=IntakeRequestRead)
def get_request(request_id: str, db: Session = Depends(get_db)) -> IntakeRequestRead:
    request = IntakeService(db).get_request(request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return request
