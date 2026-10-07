from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product
from app.models.customer import Customer
from app.schemas.order import OrderCreate, OrderResponse

from app.services.email import send_email


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


@router.post("/", response_model=OrderResponse)
def create_order(
    order: OrderCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    cart = db.query(Cart).filter(
        Cart.user_id == order.user_id
    ).first()

    if not cart:
        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )

    cart_items = db.query(CartItem).filter(
        CartItem.cart_id == cart.id
    ).all()

    if not cart_items:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty"
        )

    total_amount = 0

    new_order = Order(
        user_id=order.user_id,
        total_amount=0,
        status="Pending"
    )

    db.add(new_order)
    db.flush()

    for cart_item in cart_items:

        product = db.query(Product).filter(
            Product.id == cart_item.product_id
        ).first()

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        if product.stock < cart_item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for product {product.id}"
            )

        item_total = product.price * cart_item.quantity
        total_amount += item_total

        order_item = OrderItem(
            order_id=new_order.id,
            product_id=product.id,
            quantity=cart_item.quantity,
            price=product.price
        )

        db.add(order_item)

        product.stock -= cart_item.quantity

    new_order.total_amount = total_amount

    db.query(CartItem).filter(
        CartItem.cart_id == cart.id
    ).delete()

    db.commit()
    db.refresh(new_order)

    # Find customer email
    customer = db.query(Customer).filter(
        Customer.id == order.user_id
    ).first()

    # Send order confirmation email in background
    if customer:
        background_tasks.add_task(
            send_email,
            customer.email,
            "Order Placed Successfully",
            f"Hello {customer.name},\n\n"
            f"Your order #{new_order.id} has been placed successfully.\n\n"
            f"Order Amount: ₹{new_order.total_amount}\n"
            f"Order Status: {new_order.status}\n\n"
            "Thank you for shopping with us!"
        )

    return new_order