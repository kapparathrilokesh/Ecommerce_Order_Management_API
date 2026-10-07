from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.models.Review import Review
from app.models.order import Order
from app.models.order_item import OrderItem
from app.schemas.Review import (
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
    ReviewSummaryResponse
)
from app.auth.dependencies import require_role, get_current_user


router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)


# Customer - Create Review
@router.post(
    "/",
    response_model=ReviewResponse,
    status_code=201
)
def create_review(
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("Customer"))
):
    customer_id = int(current_user["sub"])

    # Check product exists
    product = db.query(Product).filter(
        Product.id == review_data.product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # Check customer has a delivered order containing this product
    purchased_product = (
        db.query(OrderItem)
        .join(Order, OrderItem.order_id == Order.id)
        .filter(
            Order.user_id == customer_id,
            Order.status == "Delivered",
            OrderItem.product_id == review_data.product_id
        )
        .first()
    )

    if not purchased_product:
        raise HTTPException(
            status_code=400,
            detail="You can review a product only after it has been delivered"
        )

    # Check if customer already reviewed this product
    existing_review = db.query(Review).filter(
        Review.product_id == review_data.product_id,
        Review.user_id == customer_id
    ).first()

    if existing_review:
        raise HTTPException(
            status_code=400,
            detail="You have already reviewed this product"
        )

    # Create review
    new_review = Review(
        product_id=review_data.product_id,
        user_id=customer_id,
        rating=review_data.rating,
        comment=review_data.comment
    )

    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    return new_review


# Get Reviews for a Product
@router.get(
    "/product/{product_id}",
    response_model=list[ReviewResponse]
)
def get_product_reviews(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    reviews = db.query(Review).filter(
        Review.product_id == product_id
    ).all()

    return reviews


# Get Product Review Summary
@router.get(
    "/product/{product_id}/summary",
    response_model=ReviewSummaryResponse
)
def get_review_summary(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    result = db.query(
        func.avg(Review.rating),
        func.count(Review.id)
    ).filter(
        Review.product_id == product_id
    ).first()

    average_rating = result[0]
    review_count = result[1]

    if average_rating is None:
        average_rating = 0.0

    return {
        "product_id": product_id,
        "average_rating": round(float(average_rating), 2),
        "review_count": int(review_count)
    }


# Customer - Update Own Review
@router.put(
    "/{review_id}",
    response_model=ReviewResponse
)
def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("Customer"))
):
    customer_id = int(current_user["sub"])

    review = db.query(Review).filter(
        Review.id == review_id
    ).first()

    if not review:
        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )

    # Ownership check
    if review.user_id != customer_id:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own review"
        )

    update_data = review_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(review, field, value)

    db.commit()
    db.refresh(review)

    return review


# Customer - Delete Own Review
@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("Customer"))
):
    customer_id = int(current_user["sub"])

    review = db.query(Review).filter(
        Review.id == review_id
    ).first()

    if not review:
        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )

    # Ownership check
    if review.user_id != customer_id:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own review"
        )

    db.delete(review)
    db.commit()

    return {
        "message": "Review deleted successfully"
    }