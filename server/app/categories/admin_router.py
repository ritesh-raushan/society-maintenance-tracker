import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_admin
from app.categories.schemas import (
    CategoryCreate,
    CategoryRead,
    CategoryStatusUpdate,
    CategoryUpdate,
)
from app.categories.service import (
    create_category,
    get_category_or_404,
    list_categories,
    set_category_status,
    update_category,
)
from app.database.session import get_db
from app.models import User

router = APIRouter(prefix="/admin/categories", tags=["admin"])


@router.get("", response_model=list[CategoryRead])
def list_all_categories(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return list_categories(db, active_only=False)


@router.post("", response_model=CategoryRead, status_code=201)
def create_new_category(
    payload: CategoryCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return create_category(db, payload)


@router.patch("/{category_id}", response_model=CategoryRead)
def update_existing_category(
    category_id: uuid.UUID,
    payload: CategoryUpdate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    category = get_category_or_404(db, category_id)
    return update_category(db, category, payload)


@router.patch("/{category_id}/status", response_model=CategoryRead)
def update_category_status(
    category_id: uuid.UUID,
    payload: CategoryStatusUpdate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    category = get_category_or_404(db, category_id)
    return set_category_status(db, category, payload.is_active)
