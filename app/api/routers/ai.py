from fastapi import APIRouter

from app.schemas.ai import SkillInvocationRequest, SkillInvocationResponse
from app.services.ai import AIService

router = APIRouter()


@router.get("/skills")
def list_skills() -> dict:
    return {"skills": AIService().orchestrator.list_skills()}


@router.post("/invoke", response_model=SkillInvocationResponse)
def invoke_skill(payload: SkillInvocationRequest) -> SkillInvocationResponse:
    result = AIService().invoke_skill(payload.skill_name, payload.payload)
    return SkillInvocationResponse(skill_name=payload.skill_name, status="stubbed", result=result)

