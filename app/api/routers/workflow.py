from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.services.workflow import WorkflowService

router = APIRouter()


@router.get("/requests/{request_id}/steps")
def get_workflow_steps(request_id: str, db: Session = Depends(get_db)) -> list[dict]:
    return WorkflowService(db).get_pending_steps(request_id)


@router.get("/requests/{request_id}/summary")
def workflow_summary(request_id: str, db: Session = Depends(get_db)) -> dict:
    steps = WorkflowService(db).get_pending_steps(request_id)
    return {"request_id": request_id, "steps": steps, "step_count": len(steps)}


@router.post("/requests/{request_id}/trigger")
def trigger_workflow(request_id: str, db: Session = Depends(get_db)) -> dict:
    return WorkflowService(db).trigger_external_workflow(request_id)
