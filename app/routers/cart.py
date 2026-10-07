from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.cart import Cart
from app.schemas.cart import CartCreate, CartResponse


router = APIRouter(
    prefix="/carts",
    tags=["Carts"]
)


@router.post("/", response_model=CartResponse)
def create_cart(
    cart: CartCreate,
    db: Session = Depends(get_db)
):
    existing_cart = db.query(Cart).filter(
        Cart.user_id == cart.user_id
    ).first()

    if existing_cart:
        raise HTTPException(
            status_code=400,
            detail="Cart already exists for this user"
        )

    new_cart = Cart(
        user_id=cart.user_id
    )

    db.add(new_cart)
    db.commit()
    db.refresh(new_cart)

    return new_cart


@router.get("/{cart_id}", response_model=CartResponse)
def get_cart(
    cart_id: int,
    db: Session = Depends(get_db)
):
    cart = db.query(Cart).filter(
        Cart.id == cart_id
    ).first()

    if not cart:
        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )

    return cart