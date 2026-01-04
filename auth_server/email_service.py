import smtplib
from email.mime.text import MIMEText

GMAIL_USER = "chrao7676@gmail.com"
GMAIL_APP_PASSWORD = "oelo kkdy zxgv mngj"

def send_verification_email(to_email, code):
    msg = MIMEText(f"Your AI ROBO HUB verification code is: {code}")
    msg["Subject"] = "Verify your AI ROBO HUB account"
    msg["From"] = GMAIL_USER
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.send_message(msg)
