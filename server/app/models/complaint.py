import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import BaseModel
from app.models.enums import ComplaintPriority, ComplaintStatus


class Complaint(BaseModel):
    __tablename__ = "complaints"

    resident_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id"),
        nullable=False,
        index=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    photo_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[ComplaintStatus] = mapped_column(
        SQLEnum(ComplaintStatus, name="complaint_status"),
        nullable=False,
        default=ComplaintStatus.OPEN,
        index=True,
    )

    priority: Mapped[ComplaintPriority] = mapped_column(
        SQLEnum(ComplaintPriority, name="complaint_priority"),
        nullable=False,
        default=ComplaintPriority.MEDIUM,
        index=True,
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    resident = relationship(
        "User",
        back_populates="complaints",
    )

    category = relationship(
        "Category",
        back_populates="complaints",
    )

    status_history = relationship(
        "ComplaintStatusHistory",
        back_populates="complaint",
        order_by="ComplaintStatusHistory.created_at",
    )

    __table_args__ = (
        Index(
            "ix_complaints_created_at",
            "created_at",
        ),
    )