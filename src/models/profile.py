"""Profile model — user's CV data and search preferences."""

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDMixin


class Profile(Base, UUIDMixin, TimestampMixin):
    """Stores CV content and job search preferences."""

    __tablename__ = "profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    raw_cv_text: Mapped[str | None] = mapped_column(Text)
    skills: Mapped[dict | None] = mapped_column(JSONB)
    target_roles: Mapped[dict | None] = mapped_column(JSONB)
    target_locations: Mapped[dict | None] = mapped_column(JSONB)
    salary_expectations: Mapped[dict | None] = mapped_column(JSONB)
    preferences: Mapped[dict | None] = mapped_column(JSONB)
    availability: Mapped[str | None] = mapped_column(String(50))

    # Relationships
    user: Mapped["User"] = relationship(back_populates="profile")  # noqa: F821
