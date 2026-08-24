from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import SystemSetting, User

OVERDUE_THRESHOLD_KEY = "overdue_threshold_days"
DEFAULT_OVERDUE_THRESHOLD_DAYS = 3


def get_overdue_threshold_setting(db: Session) -> SystemSetting | None:
    return db.scalar(
        select(SystemSetting).where(SystemSetting.key == OVERDUE_THRESHOLD_KEY),
    )


def get_overdue_threshold_days(db: Session) -> int:
    setting = get_overdue_threshold_setting(db)

    if setting is None:
        return DEFAULT_OVERDUE_THRESHOLD_DAYS

    try:
        days = int(setting.value)
    except (TypeError, ValueError):
        return DEFAULT_OVERDUE_THRESHOLD_DAYS

    return days if days > 0 else DEFAULT_OVERDUE_THRESHOLD_DAYS


def set_overdue_threshold(
    db: Session,
    *,
    days: int,
    actor: User,
) -> int:
    setting = get_overdue_threshold_setting(db)

    if setting is None:
        setting = SystemSetting(
            key=OVERDUE_THRESHOLD_KEY,
            value=str(days),
            updated_by=actor.id,
        )
        db.add(setting)
    else:
        setting.value = str(days)
        setting.updated_by = actor.id

    db.commit()

    return days
