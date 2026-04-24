from sqlalchemy.orm import Session, joinedload

from app.models.intake import IntakeRequest


class IntakeQueryService:
    def __init__(self, db: Session):
        self.db = db

    def list_requests(self) -> list[IntakeRequest]:
        return (
            self.db.query(IntakeRequest)
            .options(joinedload(IntakeRequest.approval_steps))
            .order_by(IntakeRequest.created_at.desc())
            .all()
        )

    def get_request(self, request_id: str) -> IntakeRequest | None:
        return (
            self.db.query(IntakeRequest)
            .options(joinedload(IntakeRequest.approval_steps))
            .filter(IntakeRequest.id == request_id)
            .first()
        )

    def get_by_request_number(self, request_number: str) -> IntakeRequest | None:
        return (
            self.db.query(IntakeRequest)
            .options(joinedload(IntakeRequest.approval_steps))
            .filter(IntakeRequest.request_number == request_number)
            .first()
        )

