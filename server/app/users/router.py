from typing import Literal

import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_admin
from app.database.session import get_db
from app.models import User
from app.schemas.pagination import (
    Page,
    build_page,
    pagination_params,
    run_paginated_query,
)
from app.users.schemas import (
    AdminUserRead,
    UserStatusRead,
    UserStatusUpdate,
)
from app.users.service import get_resident_or_404, list_residents_stmt, set_user_status

router = APIRouter(prefix="/admin/users", tags=["admin"])

SORT_COLUMNS = {
    "name": User.name,
    "email": User.email,
    "created_at": User.created_at,
}


@router.get("", response_model=Page[AdminUserRead])
def list_residents(
    search: str | None = None,
    is_active: bool | None = None,
    sort_by: Literal["name", "email", "created_at"] = "created_at",
    sort_order: Literal["asc", "desc"] = "desc",
    page_and_size: tuple[int, int] = Depends(pagination_params),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    page, page_size = page_and_size

    stmt = list_residents_stmt(
        search=search,
        is_active=is_active,
        sort_column=SORT_COLUMNS[sort_by],
        descending=sort_order == "desc",
    )

    items, total = run_paginated_query(db, stmt, page, page_size)

    return build_page(items, total, page, page_size)


@router.patch("/{user_id}/status", response_model=UserStatusRead)
def update_user_status(
    user_id: uuid.UUID,
    payload: UserStatusUpdate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    user = get_resident_or_404(db, user_id)

    user = set_user_status(db, user, payload.is_active)

    return user
