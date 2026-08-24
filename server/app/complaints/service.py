import uuid
from datetime import datetime, time, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.core.errors import AppError
from app.models import (
    Category,
    Complaint,
    ComplaintPriority,
    ComplaintStatus,
    ComplaintStatusHistory,
    User,
    UserRole,
)
from app.settings.service import get_overdue_threshold_days


def is_complaint_overdue(
    complaint: Complaint,
    threshold_days: int,
    now: datetime | None = None,
) -> bool:
    if complaint.status == ComplaintStatus.RESOLVED:
        return False

    current_time = now or datetime.now(timezone.utc)

    return current_time > complaint.created_at + timedelta(days=threshold_days)


def attach_overdue_flags(
    complaints: list[Complaint],
    db: Session,
) -> None:
    threshold = get_overdue_threshold_days(db)

    for complaint in complaints:
        complaint.is_overdue = is_complaint_overdue(complaint, threshold)


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


VALID_STATUS_TRANSITIONS: dict[ComplaintStatus, set[ComplaintStatus]] = {
    ComplaintStatus.OPEN: {
        ComplaintStatus.IN_PROGRESS,
        ComplaintStatus.RESOLVED,
    },
    ComplaintStatus.IN_PROGRESS: {ComplaintStatus.RESOLVED},
    ComplaintStatus.RESOLVED: set(),
}


complaint_status_labels = {
    ComplaintStatus.OPEN: "OPEN",
    ComplaintStatus.IN_PROGRESS: "IN_PROGRESS",
    ComplaintStatus.RESOLVED: "RESOLVED",
}


def update_complaint_status(
    db: Session,
    complaint: Complaint,
    *,
    new_status: ComplaintStatus,
    actor: User,
    note: str | None,
) -> Complaint:
    allowed = VALID_STATUS_TRANSITIONS.get(complaint.status, set())

    if new_status not in allowed:
        raise AppError(
            code="INVALID_STATUS_TRANSITION",
            message=(
                f"Cannot change complaint status from "
                f"{complaint_status_labels[complaint.status]} to "
                f"{complaint_status_labels[new_status]}."
            ),
            status_code=400,
            details={
                "current_status": complaint.status.value,
                "allowed_transitions": sorted(s.value for s in allowed) or None,
            },
        )

    old_status = complaint.status

    complaint.status = new_status

    if new_status == ComplaintStatus.RESOLVED:
        complaint.resolved_at = datetime.now(timezone.utc)

    history_record = ComplaintStatusHistory(
        complaint_id=complaint.id,
        actor_id=actor.id,
        old_status=old_status,
        new_status=new_status,
        note=note,
    )

    db.add(history_record)
    db.commit()
    db.refresh(complaint)

    return complaint


def update_complaint_priority(
    db: Session,
    complaint: Complaint,
    priority: ComplaintPriority,
) -> Complaint:
    complaint.priority = priority
    db.commit()
    db.refresh(complaint)
    return complaint


def build_overdue_condition(threshold_days: int):
    return (Complaint.status != ComplaintStatus.RESOLVED) & (
        func.now() > Complaint.created_at + func.make_interval(0, 0, 0, threshold_days)
    )


def build_admin_list_stmt(
    db: Session,
    *,
    status: ComplaintStatus | None,
    category_id: uuid.UUID | None,
    priority: ComplaintPriority | None,
    date_from,
    date_to,
    is_overdue: bool | None,
    sort_column,
    descending: bool,
):
    stmt = select(Complaint).options(
        joinedload(Complaint.category),
        joinedload(Complaint.resident),
    )

    if status is not None:
        stmt = stmt.where(Complaint.status == status)

    if category_id is not None:
        stmt = stmt.where(Complaint.category_id == category_id)

    if priority is not None:
        stmt = stmt.where(Complaint.priority == priority)

    threshold_days = get_overdue_threshold_days(db)

    overdue_condition = build_overdue_condition(threshold_days)

    if is_overdue is True:
        stmt = stmt.where(overdue_condition)
    elif is_overdue is False:
        stmt = stmt.where(~overdue_condition)

    if date_from is not None:
        stmt = stmt.where(Complaint.created_at >= datetime.combine(date_from, time.min, timezone.utc))

    if date_to is not None:
        stmt = stmt.where(
            Complaint.created_at < datetime.combine(date_to, time.min, timezone.utc) + timedelta(days=1),
        )

    stmt = stmt.order_by(sort_column.desc() if descending else sort_column.asc())

    return stmt
