"""Job model — a scraped job posting."""

from datetime import datetime

from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin, UUIDMixin


class Job(Base, UUIDMixin, TimestampMixin):
    """A job posting scraped from an external portal."""

    __tablename__ = "jobs"

    external_id: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    salary_range: Mapped[str | None] = mapped_column(String(255))
    match_score: Mapped[float | None] = mapped_column(Float)
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
