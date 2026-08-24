from datetime import date
from typing import Literal

import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_admin
from app.complaints.schemas import (
    AdminComplaintRead,
    ComplaintPriorityRead,
    ComplaintStatusRead,
    PriorityUpdateRequest,
    StatusUpdateRequest,
)
from app.complaints.service import (
    attach_overdue_flags,
    build_admin_list_stmt,
    get_complaint_for_user,
    update_complaint_priority,
    update_complaint_status,
)
from app.database.session import get_db
from app.models import (
    Complaint,
    ComplaintPriority,
    ComplaintStatus,
    User,
)
from app.schemas.pagination import (
    Page,
    build_page,
    pagination_params,
    run_paginated_query,
)

router = APIRouter(prefix="/admin/complaints", tags=["admin"])

SORT_COLUMNS = {
    "created_at": Complaint.created_at,
    "updated_at": Complaint.updated_at,
    "status": Complaint.status,
    "priority": Complaint.priority,
}


@router.get("", response_model=Page[AdminComplaintRead])
def list_all_complaints(
    status: ComplaintStatus | None = None,
    category_id: uuid.UUID | None = None,
    priority: ComplaintPriority | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    is_overdue: bool | None = None,
    sort_by: Literal["created_at", "updated_at", "status", "priority"] = "created_at",
    sort_order: Literal["asc", "desc"] = "desc",
    page_and_size: tuple[int, int] = Depends(pagination_params),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    page, page_size = page_and_size

    stmt = build_admin_list_stmt(
        db,
        status=status,
        category_id=category_id,
        priority=priority,
        date_from=date_from,
        date_to=date_to,
        is_overdue=is_overdue,
        sort_column=SORT_COLUMNS[sort_by],
        descending=sort_order == "desc",
    )

    items, total = run_paginated_query(db, stmt, page, page_size)
    attach_overdue_flags(list(items), db)

    return build_page(items, total, page, page_size)


@router.patch("/{complaint_id}/status", response_model=ComplaintStatusRead)
def update_existing_complaint_status(
    complaint_id: uuid.UUID,
    payload: StatusUpdateRequest,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    complaint = get_complaint_for_user(db, complaint_id, admin)

    complaint = update_complaint_status(
        db,
        complaint,
        new_status=payload.status,
        actor=admin,
        note=payload.note,
    )

    return complaint


@router.patch("/{complaint_id}/priority", response_model=ComplaintPriorityRead)
def update_existing_complaint_priority(
    complaint_id: uuid.UUID,
    payload: PriorityUpdateRequest,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    complaint = get_complaint_for_user(db, complaint_id, admin)

    return update_complaint_priority(db, complaint, payload.priority)
