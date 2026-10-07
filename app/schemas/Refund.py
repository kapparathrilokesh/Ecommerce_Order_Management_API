from pydantic import BaseModel, Field


class RefundCreate(BaseModel):
    payment_id: int = Field(..., gt=0)
    reason: str = Field(..., min_length=3, max_length=255)


class RefundStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(Approved|Rejected)$")
    rejection_reason: str | None = Field(
        None,
        max_length=255
    )


class RefundResponse(BaseModel):
    id: int
    payment_id: int
    amount: float
    status: str
    reason: str

    class Config:
        from_attributes = True