
from fastapi import FastAPI



# Models
from app.models.product import Product
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.payment import Payment
from app.models.Return import Return
from app.models.Refund import Refund
from app.models.Review import Review

# Routers
from app.routers.products import router as product_router
from app.routers.cart import router as cart_router
from app.routers.cart_item import router as cart_item_router
from app.routers.order import router as order_router
from app.routers.payment import router as payment_router
from app.routers.Return import router as return_router
from app.routers.Refund import router as refund_router
from app.routers.Review import router as review_router
from app.routers.email import router as email_router
from app.routers.auth import router as auth_router
from app.routers.category import router as category_router



app = FastAPI(
    title="E-Commerce Order Management API",
    version="1.0.0"
)


# Include routers
app.include_router(product_router)
app.include_router(cart_router)
app.include_router(cart_item_router)
app.include_router(order_router)
app.include_router(payment_router)
app.include_router(return_router)
app.include_router(refund_router)
app.include_router(review_router)
app.include_router(email_router)
app.include_router(auth_router)
app.include_router(category_router)

@app.get("/")
def root():
    return {
        "message": "E-Commerce Order Management API is running"
    }
