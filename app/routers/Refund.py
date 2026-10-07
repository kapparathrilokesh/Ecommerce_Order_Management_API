from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.payment import Payment
from app.models.Refund import Refund
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.schemas.Refund import (
    RefundCreate,
    RefundResponse,
    RefundStatusUpdate
)
from app.auth.dependencies import get_current_user, require_role


router = APIRouter(
    prefix="/refunds",
    tags=["Refunds"]
)


# Customer - Create Refund Request
@router.post(
    "/",
    response_model=RefundResponse,
    status_code=201
)
def create_refund(
    refund_data: RefundCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("Customer"))
):
    payment = db.query(Payment).filter(
        Payment.id == refund_data.payment_id
    ).first()

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    if payment.status != "Paid":
        raise HTTPException(
            status_code=400,
            detail="Refund can only be requested for paid payments"
        )

    # Get the order connected to the payment
    order = db.query(Order).filter(
        Order.id == payment.order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # Check customer owns the order
    if order.user_id != int(current_user["sub"]):
        raise HTTPException(
            status_code=403,
            detail="You can only request refunds for your own orders"
        )

    # Allow a new refund request if previous request was rejected
    existing_refund = db.query(Refund).filter(
        Refund.payment_id == refund_data.payment_id,
        Refund.status.in_(["Requested", "Approved"])
    ).first()

    if existing_refund:
        raise HTTPException(
            status_code=400,
            detail="Refund already requested for this payment"
        )

    new_refund = Refund(
        payment_id=payment.id,
        amount=payment.amount,
        status="Requested",
        reason=refund_data.reason
    )

    db.add(new_refund)
    db.commit()
    db.refresh(new_refund)

    return new_refund


# Customer/Admin - Get Refunds
@router.get(
    "/",
    response_model=list[RefundResponse]
)
def get_refunds(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Admin can see all refunds
    if current_user.get("role") == "Admin":
        return db.query(Refund).all()

    # Customer can see only their own refunds
    if current_user.get("role") == "Customer":

        customer_id = int(current_user["sub"])

        refunds = (
            db.query(Refund)
            .join(Payment, Refund.payment_id == Payment.id)
            .join(Order, Payment.order_id == Order.id)
            .filter(Order.user_id == customer_id)
            .all()
        )

        return refunds

    raise HTTPException(
        status_code=403,
        detail="You do not have permission to access refunds"
    )


# Admin - Approve or Reject Refund
@router.put(
    "/{refund_id}/status",
    response_model=RefundResponse
)
def update_refund_status(
    refund_id: int,
    status_data: RefundStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("Admin"))
):
    refund = db.query(Refund).filter(
        Refund.id == refund_id
    ).first()

    if not refund:
        raise HTTPException(
            status_code=404,
            detail="Refund not found"
        )

    if refund.status != "Requested":
        raise HTTPException(
            status_code=400,
            detail="Refund has already been processed"
        )

    # Rejection
    if status_data.status == "Rejected":

        if not status_data.rejection_reason:
            raise HTTPException(
                status_code=400,
                detail="Rejection reason is required"
            )

        refund.status = "Rejected"
        refund.reason = status_data.rejection_reason

        db.commit()
        db.refresh(refund)

        return refund

    # Approval
    if status_data.status == "Approved":

        payment = db.query(Payment).filter(
            Payment.id == refund.payment_id
        ).first()

        if not payment:
            raise HTTPException(
                status_code=404,
                detail="Payment not found"
            )

        order = db.query(Order).filter(
            Order.id == payment.order_id
        ).first()

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )

        # Restore product stock
        order_items = db.query(OrderItem).filter(
            OrderItem.order_id == order.id
        ).all()

        for item in order_items:

            product = db.query(Product).filter(
                Product.id == item.product_id
            ).first()

            if product:
                product.stock += item.quantity

        # Update refund and payment status
        refund.status = "Approved"
        payment.status = "Refunded"

        db.commit()
        db.refresh(refund)

        return refund