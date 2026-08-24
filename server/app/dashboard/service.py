from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.complaints.service import (
    build_overdue_condition,
    get_overdue_threshold_days,
)
from app.models import (
    Category,
    Complaint,
    ComplaintStatus,
)


def get_dashboard_stats(db: Session) -> dict:
    total_complaints = db.scalar(select(func.count()).select_from(Complaint)) or 0

    status_counts = {
        status.value if hasattr(status, "value") else str(status): count
        for status, count in db.execute(
            select(Complaint.status, func.count()).group_by(Complaint.status),
        ).all()
    }

    priority_counts = {
        priority.value if hasattr(priority, "value") else str(priority): count
        for priority, count in db.execute(
            select(Complaint.priority, func.count()).group_by(Complaint.priority),
        ).all()
    }

    category_counts = {
        name: count
        for name, count in db.execute(
            select(Category.name, func.count())
            .join(Complaint, Complaint.category_id == Category.id)
            .group_by(Category.name)
            .order_by(func.count().desc(), Category.name.asc()),
        ).all()
    }

    threshold_days = get_overdue_threshold_days(db)

    overdue = db.scalar(
        select(func.count())
        .select_from(Complaint)
        .where(build_overdue_condition(threshold_days)),
    ) or 0

    return {
        "total_complaints": total_complaints,
        "open": status_counts.get(ComplaintStatus.OPEN.value, 0),
        "in_progress": status_counts.get(ComplaintStatus.IN_PROGRESS.value, 0),
        "resolved": status_counts.get(ComplaintStatus.RESOLVED.value, 0),
        "overdue": overdue,
        "by_category": category_counts,
        "by_priority": priority_counts,
    }
