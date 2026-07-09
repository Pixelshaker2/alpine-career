"""User model — represents a Telegram bot user."""

from sqlalchemy import BigInteger, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    """A bot user identified by Telegram chat ID."""

    __tablename__ = "users"

    telegram_chat_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False, index=True
    )
    telegram_username: Mapped[str | None] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255))
    gmail_token: Mapped[dict | None] = mapped_column(JSONB)

    # Relationships
    profile: Mapped["Profile"] = relationship(  # noqa: F821
        back_populates="user", uselist=False, lazy="selectin"
    )
    applications: Mapped[list["Application"]] = relationship(  # noqa: F821
        back_populates="user", lazy="selectin"
    )
