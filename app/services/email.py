import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv


load_dotenv()


def send_email(
    to_email: str,
    subject: str,
    message: str
):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from_email = os.getenv("SMTP_FROM_EMAIL")

    if not all([
        smtp_host,
        smtp_username,
        smtp_password,
        smtp_from_email
    ]):
        print("SMTP configuration is missing.")
        return {
            "message": "Email notification could not be sent"
        }

    try:
        email_message = MIMEMultipart()
        email_message["From"] = smtp_from_email
        email_message["To"] = to_email
        email_message["Subject"] = subject

        email_message.attach(
            MIMEText(message, "plain")
        )

        with smtplib.SMTP(
            smtp_host,
            smtp_port
        ) as server:

            server.starttls()

            server.login(
                smtp_username,
                smtp_password
            )

            server.sendmail(
                smtp_from_email,
                to_email,
                email_message.as_string()
            )

        print("----- EMAIL SENT SUCCESSFULLY -----")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print("-----------------------------------")

        return {
            "message": "Email notification sent successfully"
        }

    except Exception as e:
        print("Email sending failed:", str(e))

        return {
            "message": "Email notification could not be sent"
        }