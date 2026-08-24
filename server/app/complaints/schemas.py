import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import ComplaintPriority, ComplaintStatus


class ComplaintCategoryBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str


class UserBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str


class ComplaintRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    category: ComplaintCategoryBrief
    description: str
    photo_url: str | None
    status: ComplaintStatus
    priority: ComplaintPriority
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None
    is_overdue: bool = False


class StatusHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    old_status: ComplaintStatus
    new_status: ComplaintStatus
    actor: UserBrief
    note: str | None
    created_at: datetime
