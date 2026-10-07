from sqlalchemy import Column, Integer, String, ForeignKey

from app.database import Base
from app.models.base import TimestampMixin


class Review(TimestampMixin, Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    user_id = Column(Integer, nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(String(500), nullable=True)