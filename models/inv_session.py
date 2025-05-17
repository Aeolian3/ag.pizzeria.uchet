import enum
from datetime import datetime
from enum import Enum as PyEnum
from .user import User
from sqlalchemy import (
    ForeignKey,
    DateTime,
    Numeric,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .organization import Organization
from .products import Product
from database.base import Base
from sqlalchemy import Enum as SQLAlchemyEnum


class InventoryStatus(PyEnum):
    active = "active"
    finished = "finished"
    cancelled = "cancelled"


class InventoryFrequency(enum.Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"

class InventorySession(Base):
    __tablename__ = "inventory_session"

    id: Mapped[int] = mapped_column(primary_key=True)
    pin_code: Mapped[int] = mapped_column(nullable=True)

    status = mapped_column(SQLAlchemyEnum(InventoryStatus, name="inventory_status"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    frequency: Mapped[InventoryFrequency] = mapped_column(
        SQLAlchemyEnum(InventoryFrequency, name="inventory_frequency"),
        nullable=True
    )

    creator_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    creator: Mapped["User"] = relationship(back_populates="created_sessions")

    organization_id: Mapped[int] = mapped_column(ForeignKey("organization.id"), nullable=False)
    organization: Mapped["Organization"] = relationship(back_populates="sessions")

    users: Mapped[list["InventoryUser"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    products: Mapped[list["InventoryProduct"]] = relationship(back_populates="session", cascade="all, delete-orphan")

class InventoryProduct(Base):
    __tablename__ = "inventory_product"
    __table_args__ = (
        UniqueConstraint("session_id", "product_id", name="uq_inventory_product"),
    )

    session_id: Mapped[int] = mapped_column(ForeignKey("inventory_session.id"), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    quantity: Mapped[float] = mapped_column(Numeric, nullable=False)

    session: Mapped["InventorySession"] = relationship(back_populates="products")
    product: Mapped["Product"] = relationship()
    user: Mapped["User"] = relationship(back_populates="inventory_entries")

class InventoryUser(Base):
    __tablename__ = "inventory_user"
    __table_args__ = (
        UniqueConstraint("session_id", "user_id", name="uq_inventory_user"),
    )

    session_id: Mapped[int] = mapped_column(ForeignKey("inventory_session.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    login_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped["InventorySession"] = relationship(back_populates="users")
    user: Mapped["User"] = relationship()