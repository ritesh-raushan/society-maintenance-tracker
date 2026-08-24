import uuid

from sqlalchemy import Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import BaseModel
from app.models.enums import ComplaintStatus


class ComplaintStatusHistory(BaseModel):
    __tablename__ = "complaint_status_history"

    complaint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("complaints.id"),
        nullable=False,
        index=True,
    )

    actor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    old_status: Mapped[ComplaintStatus] = mapped_column(
        SQLEnum(
            ComplaintStatus,
            name="complaint_status",
            create_type=False,
        ),
        nullable=False,
    )

    new_status: Mapped[ComplaintStatus] = mapped_column(
        SQLEnum(
            ComplaintStatus,
            name="complaint_status",
            create_type=False,
        ),
        nullable=False,
    )

    note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    complaint = relationship(
        "Complaint",
        back_populates="status_history",
    )

    actor = relationship(
        "User",
        back_populates="status_changes",
    )