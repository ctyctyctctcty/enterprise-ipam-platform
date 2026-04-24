from app.ai.orchestrator import AIOrchestrator


class AIService:
    def __init__(self):
        self.orchestrator = AIOrchestrator()

    def invoke_skill(self, skill_name: str, payload: dict) -> dict:
        return self.orchestrator.run(skill_name, payload)

