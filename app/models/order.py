from sqlalchemy import Column, Integer, Numeric, String

from app.database import Base
from app.models.base import TimestampMixin


class Order(TimestampMixin, Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False, default=0)
    status = Column(String(30), nullable=False, default="Pending")