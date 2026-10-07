from pydantic import BaseModel, Field


class CartItemCreate(BaseModel):
    cart_id: int = Field(..., gt=0)
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class CartItemResponse(BaseModel):
    id: int
    cart_id: int
    product_id: int
    quantity: int

    class Config:
        from_attributes = True