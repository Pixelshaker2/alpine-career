"""Application model — tracks a job application from start to finish."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, LargeBinary, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDMixin


class Application(Base, UUIDMixin, TimestampMixin):
    """A job application linking a user to a job posting."""

    __tablename__ = "applications"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="found"
    )
    cv_pdf: Mapped[bytes | None] = mapped_column(LargeBinary)
    cover_letter_pdf: Mapped[bytes | None] = mapped_column(LargeBinary)
    email_subject: Mapped[str | None] = mapped_column(String(500))
    email_body: Mapped[str | None] = mapped_column(Text)
    email_to: Mapped[str | None] = mapped_column(String(255))
    gmail_message_id: Mapped[str | None] = mapped_column(String(255))
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="applications")  # noqa: F821
    job: Mapped["Job"] = relationship(lazy="selectin")  # noqa: F821
