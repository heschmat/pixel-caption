import logging

from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db.models.user import User
from app.repositories.users import create_user, get_user_by_email

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    pass


class UserAlreadyExistsError(Exception):
    pass


def register_user(db: Session, *, email: str, password: str) -> User:
    existing_user = get_user_by_email(db, email)
    if existing_user:
        raise UserAlreadyExistsError("A user with this email already exists.")

    user = create_user(
        db,
        email=email,
        hashed_password=hash_password(password),
    )

    logger.info("user_registered", extra={"user_id": user.id, "email": user.email})
    return user


def authenticate_user(db: Session, *, email: str, password: str) -> str:
    user = get_user_by_email(db, email)
    if not user:
        raise AuthenticationError("Invalid email or password.")

    if not verify_password(password, user.hashed_password):
        raise AuthenticationError("Invalid email or password.")

    if not user.is_active:
        raise AuthenticationError("User is inactive.")

    token = create_access_token(str(user.id))
    logger.info("user_authenticated", extra={"user_id": user.id, "email": user.email})
    return token
