from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.order import Order
from app.models.Return import Return
from app.schemas.Return import ReturnCreate, ReturnResponse


router = APIRouter(
    prefix="/returns",
    tags=["Returns"]
)


@router.post("/", response_model=ReturnResponse)
def create_return(
    return_data: ReturnCreate,
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(
        Order.id == return_data.order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if order.status not in ["Paid", "Delivered"]:
        raise HTTPException(
            status_code=400,
            detail="Return can only be requested for paid or delivered orders"
        )

    existing_return = db.query(Return).filter(
        Return.order_id == return_data.order_id
    ).first()

    if existing_return:
        raise HTTPException(
            status_code=400,
            detail="Return already requested for this order"
        )

    new_return = Return(
        order_id=return_data.order_id,
        reason=return_data.reason,
        status="Requested"
    )

    db.add(new_return)
    db.commit()
    db.refresh(new_return)

    return new_return