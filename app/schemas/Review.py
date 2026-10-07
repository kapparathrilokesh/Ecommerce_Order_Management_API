from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = Field(None, max_length=500)


class ReviewUpdate(BaseModel):
    rating: int | None = Field(None, ge=1, le=5)
    comment: str | None = Field(None, max_length=500)


class ReviewResponse(BaseModel):
    id: int
    product_id: int
    user_id: int
    rating: int
    comment: str | None

    class Config:
        from_attributes = True


class ReviewSummaryResponse(BaseModel):
    product_id: int
    average_rating: float
    review_count: int