import uuid

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_admin
from app.database.session import get_db
from app.models import User
from app.notices.schemas import NoticeCreate, NoticeRead, NoticeUpdate
from app.notices.service import (
    create_notice,
    delete_notice,
    get_notice_or_404,
    update_notice,
)

router = APIRouter(prefix="/admin/notices", tags=["admin"])


@router.post("", response_model=NoticeRead, status_code=201)
def create_new_notice(
    payload: NoticeCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return create_notice(db, author=admin, data=payload)


@router.patch("/{notice_id}", response_model=NoticeRead)
def update_existing_notice(
    notice_id: uuid.UUID,
    payload: NoticeUpdate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    notice = get_notice_or_404(db, notice_id)

    return update_notice(db, notice, payload)


@router.delete("/{notice_id}", status_code=204)
def delete_existing_notice(
    notice_id: uuid.UUID,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    notice = get_notice_or_404(db, notice_id)

    delete_notice(db, notice)

    return Response(status_code=204)
