from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from database.base import Base

if TYPE_CHECKING:
    from .category import Category
    from .user import User
    from .inv_session import InventorySession
    from .products import Product

class Organization(Base):
    __tablename__ = "organization"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    categories: Mapped[list["Category"]] = relationship(back_populates="organization")
    users: Mapped[list["User"]] = relationship(back_populates="organization")
    sessions: Mapped[list["InventorySession"]] = relationship(back_populates="organization")
    products: Mapped[list["Product"]] = relationship(back_populates="organization")
