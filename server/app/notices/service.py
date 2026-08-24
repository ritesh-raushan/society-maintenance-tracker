import uuid

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models import Notice, User
from app.notices.schemas import NoticeCreate, NoticeUpdate


def get_notice_or_404(db: Session, notice_id: uuid.UUID) -> Notice:
    notice = db.get(Notice, notice_id)

    if notice is None:
        raise AppError(
            code="NOTICE_NOT_FOUND",
            message="Notice not found.",
            status_code=404,
        )

    return notice


def list_notices_stmt() -> Select:
    return select(Notice).order_by(
        Notice.is_important.desc(),
        Notice.created_at.desc(),
    )


def create_notice(db: Session, *, author: User, data: NoticeCreate) -> Notice:
    notice = Notice(
        admin_id=author.id,
        title=data.title.strip(),
        content=data.content.strip(),
        is_important=data.is_important,
    )

    db.add(notice)
    db.commit()
    db.refresh(notice)

    return notice


def update_notice(
    db: Session,
    notice: Notice,
    data: NoticeUpdate,
) -> Notice:
    changes = data.model_dump(exclude_unset=True)

    if changes.get("title") is not None:
        notice.title = changes["title"].strip()

    if changes.get("content") is not None:
        notice.content = changes["content"].strip()

    if changes.get("is_important") is not None:
        notice.is_important = changes["is_important"]

    db.commit()
    db.refresh(notice)

    return notice


def delete_notice(db: Session, notice: Notice) -> None:
    db.delete(notice)
    db.commit()
