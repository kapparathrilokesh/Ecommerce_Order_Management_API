from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.customer import Customer

from app.auth.dependencies import (
    get_current_user,
    require_role
)

from app.schemas.customer import (
    CustomerCreate,
    CustomerResponse
)

from app.schemas.auth import (
    LoginRequest,
    TokenResponse
)

from app.auth.security import (
    hash_password,
    verify_password
)

from app.auth.jwt import create_access_token

from app.services.email import send_email


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# -----------------------------
# Customer Registration
# -----------------------------

@router.post(
    "/register",
    response_model=CustomerResponse,
    status_code=201
)
def register_customer(
    customer_data: CustomerCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    existing_customer = db.query(Customer).filter(
        Customer.email == customer_data.email
    ).first()

    if existing_customer:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = hash_password(
        customer_data.password
    )

    customer = Customer(
        name=customer_data.name,
        email=customer_data.email,
        password=hashed_password,
        role="Customer",
        is_active=True
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    # Send registration email in the background
    background_tasks.add_task(
        send_email,
        customer.email,
        "Welcome to E-Commerce Order Management",
        f"Hello {customer.name},\n\n"
        "Your account has been successfully registered.\n\n"
        "Thank you for joining us!"
    )

    return customer


# -----------------------------
# Customer Login
# -----------------------------

@router.post(
    "/login",
    response_model=TokenResponse
)
def login_customer(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    customer = db.query(Customer).filter(
        Customer.email == login_data.email
    ).first()

    if not customer:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        login_data.password,
        customer.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not customer.is_active:
        raise HTTPException(
            status_code=403,
            detail="Customer account is inactive"
        )

    access_token = create_access_token(
        {
            "sub": str(customer.id),
            "role": customer.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# -----------------------------
# Get Current Customer
# -----------------------------

@router.get(
    "/me",
    response_model=CustomerResponse
)
def get_me(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = int(current_user["sub"])

    customer = db.query(Customer).filter(
        Customer.id == user_id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return customer


# -----------------------------
# Customer Protected Test
# -----------------------------

@router.get(
    "/customer-test"
)
def customer_test(
    current_user: dict = Depends(
        require_role("Customer")
    )
):
    return {
        "message": "Customer access granted",
        "user_id": current_user["sub"],
        "role": current_user["role"]
    }


# -----------------------------
# Admin Protected Test
# -----------------------------

@router.get(
    "/admin-test"
)
def admin_test(
    current_user: dict = Depends(
        require_role("Admin")
    )
):
    return {
        "message": "Admin access granted",
        "user_id": current_user["sub"],
        "role": current_user["role"]
    }