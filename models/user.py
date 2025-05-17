from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey,BigInteger
from sqlalchemy.orm import relationship, Mapped, mapped_column
from database.base import Base

if TYPE_CHECKING:
    from .roles import Role
    from .organization import Organization
    from .inv_session import InventorySession, InventoryProduct
    from .logger import Logger

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)

    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    role: Mapped["Role"] = relationship(back_populates="users")

    organization_id: Mapped[int] = mapped_column(ForeignKey("organization.id"), nullable=False)
    organization: Mapped["Organization"] = relationship(back_populates="users")

    created_sessions: Mapped[list["InventorySession"]] = relationship(back_populates="creator", cascade="all, delete-orphan")
    inventory_entries: Mapped[list["InventoryProduct"]] = relationship(back_populates="user")
    logger_entries: Mapped[list["Logger"]] = relationship(back_populates="user")
