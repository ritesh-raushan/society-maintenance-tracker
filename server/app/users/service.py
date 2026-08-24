import uuid

from sqlalchemy import Select, or_, select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models import User, UserRole


def get_resident_or_404(db: Session, user_id: uuid.UUID) -> User:
    user = db.get(User, user_id)

    if user is None or user.role != UserRole.RESIDENT:
        raise AppError(
            code="USER_NOT_FOUND",
            message="User not found.",
            status_code=404,
        )

    return user


def list_residents_stmt(
    *,
    search: str | None,
    is_active: bool | None,
    sort_column,
    descending: bool,
) -> Select:
    stmt = select(User).where(User.role == UserRole.RESIDENT)

    if search:
        pattern = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                User.name.ilike(pattern),
                User.email.ilike(pattern),
            ),
        )

    if is_active is not None:
        stmt = stmt.where(User.is_active.is_(is_active))

    stmt = stmt.order_by(sort_column.desc() if descending else sort_column.asc())

    return stmt


def set_user_status(db: Session, user: User, is_active: bool) -> User:
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user
