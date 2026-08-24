from typing import Literal

import uuid
from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user, require_resident
from app.complaints.schemas import ComplaintRead, StatusHistoryRead
from app.complaints.service import (
    create_complaint,
    get_active_category_or_error,
    get_complaint_for_user,
    get_overdue_threshold_days,
    is_complaint_overdue,
    list_resident_complaints,
)
from app.database.session import get_db
from app.models import (
    Complaint,
    ComplaintPriority,
    ComplaintStatus,
    User,
)
from app.schemas.pagination import Page, pagination_params, run_paginated_query
from app.schemas.pagination import build_page
from app.uploads.service import upload_photo, validate_photo

router = APIRouter(prefix="/complaints", tags=["complaints"])

SORT_COLUMNS = {
    "created_at": Complaint.created_at,
    "updated_at": Complaint.updated_at,
    "status": Complaint.status,
    "priority": Complaint.priority,
}


def _attach_overdue_flag(
    complaints: list[Complaint],
    db: Session,
) -> None:
    threshold = get_overdue_threshold_days(db)

    for complaint in complaints:
        complaint.is_overdue = is_complaint_overdue(complaint, threshold)


@router.post("", response_model=ComplaintRead, status_code=201)
def create_new_complaint(
    category_id: uuid.UUID = Form(...),
    description: str = Form(min_length=1),
    photo: UploadFile | None = File(default=None),
    resident: User = Depends(require_resident),
    db: Session = Depends(get_db),
):
    category = get_active_category_or_error(db, category_id)

    photo_url = None

    if photo is not None and photo.filename:
        validate_photo(photo)
        photo_url = upload_photo(photo)

    complaint = create_complaint(
        db,
        resident=resident,
        category=category,
        description=description,
        photo_url=photo_url,
    )

    return ComplaintRead(
        id=complaint.id,
        category=category,
        description=complaint.description,
        photo_url=complaint.photo_url,
        status=complaint.status,
        priority=complaint.priority,
        created_at=complaint.created_at,
        updated_at=complaint.updated_at,
        resolved_at=complaint.resolved_at,
        is_overdue=is_complaint_overdue(
            complaint,
            get_overdue_threshold_days(db),
        ),
    )


@router.get("", response_model=Page[ComplaintRead])
def list_my_complaints(
    status: ComplaintStatus | None = None,
    category_id: uuid.UUID | None = None,
    priority: ComplaintPriority | None = None,
    sort_by: Literal["created_at", "updated_at", "status", "priority"] = "created_at",
    sort_order: Literal["asc", "desc"] = "desc",
    page_and_size: tuple[int, int] = Depends(pagination_params),
    resident: User = Depends(require_resident),
    db: Session = Depends(get_db),
):
    page, page_size = page_and_size

    stmt = list_resident_complaints(
        db,
        resident_id=resident.id,
        status=status,
        category_id=category_id,
        priority=priority,
        sort_column=SORT_COLUMNS[sort_by],
        descending=sort_order == "desc",
    )

    items, total = run_paginated_query(db, stmt, page, page_size)
    _attach_overdue_flag(list(items), db)

    return build_page(items, total, page, page_size)


@router.get("/{complaint_id}", response_model=ComplaintRead)
def get_complaint_detail(
    complaint_id: uuid.UUID,
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    complaint = get_complaint_for_user(db, complaint_id, user)
    _attach_overdue_flag([complaint], db)

    return complaint


@router.get("/{complaint_id}/history", response_model=list[StatusHistoryRead])
def get_complaint_history(
    complaint_id: uuid.UUID,
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    complaint = get_complaint_for_user(db, complaint_id, user)

    return list(complaint.status_history)
