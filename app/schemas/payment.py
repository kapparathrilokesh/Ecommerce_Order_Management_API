from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    order_id: int = Field(..., gt=0)
    payment_method: str = Field(..., min_length=2, max_length=30)


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    amount: float
    status: str
    payment_method: str

    class Config:
        from_attributes = True