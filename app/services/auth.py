from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.models.auth import User


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate(self, username: str, password: str) -> str | None:
        user = self.db.query(User).filter(User.email == username).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return create_access_token(user.email)

