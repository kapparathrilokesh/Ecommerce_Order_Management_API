from pydantic import BaseModel, Field


class CartCreate(BaseModel):
    user_id: int = Field(..., gt=0)


class CartResponse(BaseModel):
    id: int
    user_id: int

    class Config:
        from_attributes = True