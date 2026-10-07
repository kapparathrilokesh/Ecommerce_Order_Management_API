from pydantic import BaseModel, Field


class ReturnCreate(BaseModel):
    order_id: int = Field(..., gt=0)
    reason: str = Field(..., min_length=3, max_length=255)


class ReturnResponse(BaseModel):
    id: int
    order_id: int
    reason: str
    status: str

    class Config:
        from_attributes = True