from pydantic import BaseModel


class SkillInvocationRequest(BaseModel):
    skill_name: str
    payload: dict = {}


class SkillInvocationResponse(BaseModel):
    skill_name: str
    status: str
    result: dict

