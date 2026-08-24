import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.errors import AppError
from app.models import (
    Category,
    Complaint,
    ComplaintPriority,
    ComplaintStatus,
    SystemSetting,
    User,
    UserRole,
)

OVERDUE_THRESHOLD_KEY = "overdue_threshold_days"
DEFAULT_OVERDUE_THRESHOLD_DAYS = 3


def get_overdue_threshold_days(db: Session) -> int:
    setting = db.scalar(
        select(SystemSetting).where(SystemSetting.key == OVERDUE_THRESHOLD_KEY),
    )

    if setting is None:
        return DEFAULT_OVERDUE_THRESHOLD_DAYS

    try:
        days = int(setting.value)
    except (TypeError, ValueError):
        return DEFAULT_OVERDUE_THRESHOLD_DAYS

    return days if days > 0 else DEFAULT_OVERDUE_THRESHOLD_DAYS


def is_complaint_overdue(
    complaint: Complaint,
    threshold_days: int,
    now: datetime | None = None,
) -> bool:
    if complaint.status == ComplaintStatus.RESOLVED:
        return False

    current_time = now or datetime.now(timezone.utc)

    return current_time > complaint.created_at + timedelta(days=threshold_days)


def get_active_category_or_error(db: Session, category_id: uuid.UUID) -> Category:
    category = db.get(Category, category_id)

    if category is None:
        raise AppError(
            code="CATEGORY_NOT_FOUND",
            message="Category not found.",
            status_code=404,
        )

    if not category.is_active:
        raise AppError(
            code="CATEGORY_INACTIVE",
            message="This category is no longer available for new complaints.",
            status_code=400,
        )

    return category


def create_complaint(
    db: Session,
    *,
    resident: User,
    category: Category,
    description: str,
    photo_url: str | None,
) -> Complaint:
    complaint = Complaint(
        resident_id=resident.id,
        category_id=category.id,
        description=description.strip(),
        photo_url=photo_url,
        status=ComplaintStatus.OPEN,
        priority=ComplaintPriority.MEDIUM,
    )

    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    return complaint


def get_complaint_for_user(
    db: Session,
    complaint_id: uuid.UUID,
    user: User,
) -> Complaint:
    complaint = db.get(Complaint, complaint_id)

    if complaint is None:
        raise AppError(
            code="COMPLAINT_NOT_FOUND",
            message="Complaint not found.",
            status_code=404,
        )

    if user.role != UserRole.ADMIN and complaint.resident_id != user.id:
        raise AppError(
            code="COMPLAINT_NOT_FOUND",
            message="Complaint not found.",
            status_code=404,
        )

    return complaint


def list_resident_complaints(
    db: Session,
    *,
    resident_id: uuid.UUID,
    status: ComplaintStatus | None = None,
    category_id: uuid.UUID | None = None,
    priority: ComplaintPriority | None = None,
    sort_column,
    descending: bool,
):
    stmt = (
        select(Complaint)
        .options(joinedload(Complaint.category))
        .where(Complaint.resident_id == resident_id)
    )

    if status is not None:
        stmt = stmt.where(Complaint.status == status)

    if category_id is not None:
        stmt = stmt.where(Complaint.category_id == category_id)

    if priority is not None:
        stmt = stmt.where(Complaint.priority == priority)

    stmt = stmt.order_by(sort_column.desc() if descending else sort_column.asc())

    return stmt
