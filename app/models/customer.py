from sqlalchemy import Column, Integer, String, Boolean

from app.database import Base
from app.models.base import TimestampMixin


class Customer(TimestampMixin, Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(150),
        unique=True,
        nullable=False,
        index=True
    )

    password = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(20),
        nullable=False,
        default="Customer"
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True
    )