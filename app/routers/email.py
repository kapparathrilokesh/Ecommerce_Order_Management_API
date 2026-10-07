from fastapi import APIRouter
from pydantic import BaseModel, EmailStr, Field

from app.services.email import send_email


router = APIRouter(
    prefix="/notifications",
    tags=["Email Notifications"]
)


class EmailNotificationCreate(BaseModel):
    to_email: EmailStr
    subject: str = Field(..., min_length=2, max_length=150)
    message: str = Field(..., min_length=1)


@router.post("/email")
def send_email_notification(
    email_data: EmailNotificationCreate
):
    result = send_email(
        to_email=email_data.to_email,
        subject=email_data.subject,
        message=email_data.message
    )

    return result