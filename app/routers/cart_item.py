from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product
from app.schemas.cart_item import CartItemCreate, CartItemResponse


router = APIRouter(
    prefix="/cart-items",
    tags=["Cart Items"]
)


@router.post("/", response_model=CartItemResponse)
def add_cart_item(
    item: CartItemCreate,
    db: Session = Depends(get_db)
):
    cart = db.query(Cart).filter(
        Cart.id == item.cart_id
    ).first()

    if not cart:
        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )

    product = db.query(Product).filter(
        Product.id == item.product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    if not product.is_active:
        raise HTTPException(
            status_code=400,
            detail="Product is inactive"
        )

    if product.stock < item.quantity:
        raise HTTPException(
            status_code=400,
            detail="Insufficient product stock"
        )

    new_item = CartItem(
        cart_id=item.cart_id,
        product_id=item.product_id,
        quantity=item.quantity
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item

@router.get("/{cart_id}", response_model=list[CartItemResponse])
def get_cart_items(
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

    return db.query(CartItem).filter(
        CartItem.cart_id == cart_id
    ).all()