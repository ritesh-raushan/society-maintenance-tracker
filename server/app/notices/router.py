from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.database.session import get_db
from app.models import User
from app.notices.schemas import NoticeRead
from app.notices.service import list_notices_stmt
from app.schemas.pagination import (
    Page,
    build_page,
    pagination_params,
    run_paginated_query,
)

router = APIRouter(prefix="/notices", tags=["notices"])


@router.get("", response_model=Page[NoticeRead])
def list_notices(
    page_and_size: tuple[int, int] = Depends(pagination_params),
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    page, page_size = page_and_size

    stmt = list_notices_stmt()
    items, total = run_paginated_query(db, stmt, page, page_size)

    return build_page(items, total, page, page_size)
