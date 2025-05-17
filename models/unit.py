from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from database.base import Base

if TYPE_CHECKING:
    from .products import Product

class Unit(Base):
    __tablename__ = "unit"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    products: Mapped[list["Product"]] = relationship(back_populates="unit")
