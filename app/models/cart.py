from sqlalchemy import Column, Integer

from app.database import Base
from app.models.base import TimestampMixin


class Cart(TimestampMixin, Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)