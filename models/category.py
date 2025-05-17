from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from database.base import Base

if TYPE_CHECKING:
    from .organization import Organization
    from .products import Product

class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    organization_id: Mapped[int] = mapped_column(ForeignKey("organization.id", ondelete="CASCADE"))
    organization: Mapped["Organization"] = relationship(back_populates="categories")

    products: Mapped[list["Product"]] = relationship(back_populates="category")
