from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.categories.schemas import CategoryRead
from app.categories.service import list_categories
from app.database.session import get_db
from app.models import User

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryRead])
def list_active_categories(
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return list_categories(db, active_only=True)
