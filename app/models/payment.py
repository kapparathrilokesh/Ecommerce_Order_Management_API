from sqlalchemy import Column, Integer, Numeric, String, ForeignKey

from app.database import Base
from app.models.base import TimestampMixin


class Payment(TimestampMixin, Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(30), nullable=False, default="Pending")
    payment_method = Column(String(30), nullable=False)