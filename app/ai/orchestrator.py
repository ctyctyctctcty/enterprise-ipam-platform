from app.ai.registry import SKILL_REGISTRY


class AIOrchestrator:
    def list_skills(self) -> list[str]:
        return sorted(SKILL_REGISTRY.keys())

    def run(self, skill_name: str, payload: dict) -> dict:
        handler = SKILL_REGISTRY.get(skill_name)
        if not handler:
            return {"status": "missing", "message": f"Unknown skill: {skill_name}"}
        return handler(payload)

