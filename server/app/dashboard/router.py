from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_admin
from app.dashboard.schemas import DashboardRead
from app.dashboard.service import get_dashboard_stats
from app.database.session import get_db
from app.models import User

router = APIRouter(prefix="/admin/dashboard", tags=["admin"])


@router.get("", response_model=DashboardRead)
def get_admin_dashboard(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return get_dashboard_stats(db)
