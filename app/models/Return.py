from sqlalchemy import Column, Integer, String, ForeignKey

from app.database import Base
from app.models.base import TimestampMixin


class Return(TimestampMixin, Base):
    __tablename__ = "returns"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    reason = Column(String(255), nullable=False)
    status = Column(String(30), nullable=False, default="Requested")