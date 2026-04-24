from sqlalchemy.orm import Session

from app.core.enums import RequestStatus
from app.schemas.intake import IntakeRequestSubmit
from app.services.intake_commands import IntakeSubmissionService
from app.services.intake_queries import IntakeQueryService


class IntakeService:
    def __init__(self, db: Session):
        self.db = db
        self.queries = IntakeQueryService(db)
        self.commands = IntakeSubmissionService(db)

    def list_requests(self):
        return self.queries.list_requests()

    def get_request(self, request_id: str):
        return self.queries.get_request(request_id)

    def get_by_request_number(self, request_number: str):
        return self.queries.get_by_request_number(request_number)

    def create_request(self, payload: IntakeRequestSubmit):
        return self.commands.submit_request(payload)

    def evaluate_request(self, request_id: str):
        return self.commands.evaluate_request(request_id)

    def transition_request(self, request_id: str, target_status: RequestStatus, comment: str | None = None):
        return self.commands.transition_request(request_id, target_status, comment)
