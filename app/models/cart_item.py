from sqlalchemy import Column, Integer, ForeignKey

from app.database import Base
from app.models.base import TimestampMixin


class CartItem(TimestampMixin, Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)