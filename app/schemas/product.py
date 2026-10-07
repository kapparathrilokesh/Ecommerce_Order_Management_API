from decimal import Decimal
from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    sku: str = Field(..., min_length=2, max_length=100)
    description: str | None = None
    category_id: int
    price: Decimal = Field(..., gt=0)
    stock: int = Field(..., ge=0)


class ProductUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=150)
    description: str | None = None
    category_id: int | None = None
    price: Decimal | None = Field(None, gt=0)
    stock: int | None = Field(None, ge=0)
    is_active: bool | None = None


class ProductResponse(BaseModel):
    id: int
    name: str
    sku: str
    description: str | None
    category_id: int
    price: Decimal
    stock: int
    is_active: bool

    class Config:
        from_attributes = True