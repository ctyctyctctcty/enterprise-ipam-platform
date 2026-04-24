class PowerAppsAdapter:
    def receive_request(self, payload: dict) -> dict:
        return {"status": "stubbed", "message": "Future Power Apps intake adapter"}


class PowerAutomateAdapter:
    def start_workflow(self, payload: dict) -> dict:
        return {"status": "stubbed", "message": "Future Power Automate workflow adapter"}


class EntraIDAdapter:
    def resolve_user(self, subject: str) -> dict:
        return {"status": "stubbed", "subject": subject, "message": "Future Entra ID / SSO adapter"}

