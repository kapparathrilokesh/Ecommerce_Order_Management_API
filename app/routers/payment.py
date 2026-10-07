from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.payment import Payment
from app.models.order import Order
from app.models.customer import Customer
from app.schemas.payment import PaymentCreate, PaymentResponse

from app.services.email import send_email


router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)


@router.post(
    "/",
    response_model=PaymentResponse
)
def create_payment(
    payment: PaymentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(
        Order.id == payment.order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if order.status != "Pending":
        raise HTTPException(
            status_code=400,
            detail="Payment can only be made for pending orders"
        )

    existing_payment = db.query(Payment).filter(
        Payment.order_id == payment.order_id
    ).first()

    if existing_payment:
        raise HTTPException(
            status_code=400,
            detail="Payment already exists for this order"
        )

    new_payment = Payment(
        order_id=order.id,
        amount=order.total_amount,
        status="Paid",
        payment_method=payment.payment_method
    )

    order.status = "Paid"

    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    # Find customer
    customer = db.query(Customer).filter(
        Customer.id == order.user_id
    ).first()

    # Send payment success email
    if customer:
        background_tasks.add_task(
            send_email,
            customer.email,
            "Payment Successful",
            f"Hello {customer.name},\n\n"
            f"Your payment for order #{order.id} was successful.\n\n"
            f"Amount Paid: ₹{new_payment.amount}\n"
            f"Payment Method: {new_payment.payment_method}\n"
            f"Payment Status: {new_payment.status}\n\n"
            "Thank you for your payment!"
        )

    return new_payment