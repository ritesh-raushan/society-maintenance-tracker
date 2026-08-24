from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import hash_password, verify_password
from app.models import User, UserRole
from app.schemas.user import UserCreate


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


def register_user(db: Session, data: UserCreate) -> User:
    if get_user_by_email(db, data.email) is not None:
        raise AppError(
            code="EMAIL_ALREADY_EXISTS",
            message="An account with this email already exists.",
            status_code=409,
        )

    user = User(
        name=data.name.strip(),
        email=data.email.lower(),
        password_hash=hash_password(data.password),
        role=UserRole.RESIDENT,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = get_user_by_email(db, email)

    if user is None or not verify_password(password, user.password_hash):
        raise AppError(
            code="INVALID_CREDENTIALS",
            message="Incorrect email or password.",
            status_code=401,
        )

    if not user.is_active:
        raise AppError(
            code="ACCOUNT_INACTIVE",
            message="This account has been deactivated. Contact an administrator.",
            status_code=401,
        )

    return user
