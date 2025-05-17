from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from .unit import Unit
    from .category import Category
    from .organization import Organization

class Product(Base):
    __tablename__ = "product"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    category_id: Mapped[int] = mapped_column(ForeignKey("category.id", ondelete="CASCADE"), nullable=False)
    unit_id: Mapped[int] = mapped_column(ForeignKey("unit.id"), nullable=False)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organization.id", ondelete="CASCADE"), nullable=False)

    category: Mapped["Category"] = relationship(back_populates="products")
    unit: Mapped["Unit"] = relationship(back_populates="products")
    organization: Mapped["Organization"] = relationship(back_populates="products")
