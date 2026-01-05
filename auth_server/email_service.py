
# GMAIL_USER = "chrao7676@gmail.com"
# GMAIL_APP_PASSWORD = "oelo kkdy zxgv mngj"


import smtplib
from email.mime.text import MIMEText

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "chrao7676@gmail.com"
SMTP_PASS = "oelo kkdy zxgv mngj"

def send_activation_email(email, token):
    activation_link = f"http://127.0.0.1:8000/verify?token={token}"

    msg = MIMEText(f"""
Welcome to AI ROBO HUB  - QR Automation Platform

Click below to activate your account:
{activation_link}

Regards,
AI ROBO HUB Team
""")

    msg["Subject"] = "Activate your AI ROBO HUB account"
    msg["From"] = SMTP_USER
    msg["To"] = email

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USER, SMTP_PASS)
    server.sendmail(SMTP_USER, email, msg.as_string())
    server.quit()
