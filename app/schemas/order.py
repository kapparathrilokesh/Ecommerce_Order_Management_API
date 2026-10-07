from pydantic import BaseModel


class OrderCreate(BaseModel):
    user_id: int


class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_amount: float
    status: str

    class Config:
        from_attributes = True