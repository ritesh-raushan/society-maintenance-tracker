import uuid

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import decode_access_token
from app.database.session import get_db
from app.models import User, UserRole

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise AppError(
            code="NOT_AUTHENTICATED",
            message="Authentication credentials were not provided.",
            status_code=401,
        )

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = uuid.UUID(str(payload.get("sub")))
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValueError):
        raise AppError(
            code="INVALID_TOKEN",
            message="The access token is invalid or has expired.",
            status_code=401,
        )

    user = db.get(User, user_id)

    if user is None:
        raise AppError(
            code="NOT_AUTHENTICATED",
            message="The user associated with this token no longer exists.",
            status_code=401,
        )

    return user


def get_current_active_user(
    user: User = Depends(get_current_user),
) -> User:
    if not user.is_active:
        raise AppError(
            code="ACCOUNT_DEACTIVATED",
            message="This account has been deactivated.",
            status_code=403,
        )

    return user


def get_current_admin(user: User = Depends(get_current_active_user)) -> User:
    if user.role != UserRole.ADMIN:
        raise AppError(
            code="FORBIDDEN",
            message="You do not have permission to perform this action.",
            status_code=403,
        )

    return user


def require_resident(user: User = Depends(get_current_active_user)) -> User:
    if user.role != UserRole.RESIDENT:
        raise AppError(
            code="FORBIDDEN",
            message="This action is only available to residents.",
            status_code=403,
        )

    return user
