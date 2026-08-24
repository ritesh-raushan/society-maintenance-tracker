from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_admin
from app.database.session import get_db
from app.models import User
from app.settings.schemas import AdminSettingsRead, OverdueThresholdUpdate
from app.settings.service import get_overdue_threshold_days, set_overdue_threshold

router = APIRouter(prefix="/admin/settings", tags=["admin"])


@router.get("", response_model=AdminSettingsRead)
def get_admin_settings(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return AdminSettingsRead(overdue_threshold_days=get_overdue_threshold_days(db))


@router.patch("/overdue-threshold", response_model=AdminSettingsRead)
def update_overdue_threshold(
    payload: OverdueThresholdUpdate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    days = set_overdue_threshold(db, days=payload.days, actor=admin)

    return AdminSettingsRead(overdue_threshold_days=days)
