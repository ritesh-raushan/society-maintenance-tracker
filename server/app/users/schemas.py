from datetime import datetime
import uuid

from pydantic import BaseModel

from app.schemas.user import UserRead


class AdminUserRead(UserRead):
    created_at: datetime


class UserStatusUpdate(BaseModel):
    is_active: bool


class UserStatusRead(BaseModel):
    id: uuid.UUID
    is_active: bool
