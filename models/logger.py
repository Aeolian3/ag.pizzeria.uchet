from datetime import datetime
from .user import User
from sqlalchemy import (
    String,
    ForeignKey,
    DateTime,
    Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class Logger(Base):
    __tablename__ = "logger"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False)
    target_id: Mapped[int] = mapped_column(nullable=True)
    target_type: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    details: Mapped[str] = mapped_column(Text)

    user: Mapped["User"] = relationship(back_populates="logger_entries")