from http import server
import os, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# from dotenv import load_dotenv

import os

# load_dotenv()
# FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL")


MAIL_HOST = os.getenv("MAIL_HOST")
MAIL_PORT = os.getenv("MAIL_PORT")
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")


SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL")
SUPPORT_MOBILE = os.getenv("SUPPORT_MOBILE")
COMPANY_NAME = os.getenv("COMPANY_NAME")
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL")

if not all([MAIL_HOST, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD]):
    raise RuntimeError(
        f"SMTP not configured properly: "
        f"MAIL_HOST={MAIL_HOST}, MAIL_PORT={MAIL_PORT}, "
        f"MAIL_USERNAME={MAIL_USERNAME}, MAIL_PASSWORD={'SET' if MAIL_PASSWORD else None}"
    )



def send_activation_email(to_email: str, name: str, token: str, mode: str = "activate"):
    if mode == "activate":
        link = f"{FASTAPI_BASE_URL}/verify?token={token}"
        subject = f"Activate Your {COMPANY_NAME} Account"
        action_text = "Activate My Account"
        intro = f"Thank you for registering with <b>{COMPANY_NAME}</b>. Please activate your account using the button below:"
    
    elif mode == "lead_followup":
        link = FASTAPI_BASE_URL
        subject = "Regarding your AI ROBO HUB QR Automation Request"
        action_text = "Contact Support"
        intro = token

    else:  # set_password
        link = f"{FASTAPI_BASE_URL}/set-password?token={token}"
        subject = f"Set Your {COMPANY_NAME} Password"
        action_text = "Set My Password"
        intro = f"Your paid account is ready. Please set your password using the button below:"

    html = f"""
    <html>
    <body style="font-family:Arial; background:#f4f6f8; padding:20px;">
      <div style="max-width:600px; margin:auto; background:white; padding:25px; border-radius:8px;">
        <h2 style="color:#2b5cff;">Welcome to {COMPANY_NAME} 🚀</h2>

        <p>Hi <b>{name}</b>,</p>

        <p>{intro}</p>

        <div style="text-align:center; margin:30px;">
          <a href="{link}"
             style="background:#2b5cff; color:white; padding:12px 24px;
             text-decoration:none; border-radius:5px;">
             {action_text}
          </a>
        </div>

        <p>This link will expire in <b>30 minutes</b>.</p>

        <hr>

        <p style="font-size:13px; color:#666;">
        Need help? Contact our support team:<br>
        📧 {SUPPORT_EMAIL}<br>
        📞 {SUPPORT_MOBILE}
        </p>

        <p style="font-size:12px; color:#999;">© {COMPANY_NAME}</p>
      </div>
    </body>
    </html>
    """


    msg = MIMEMultipart("alternative")
    # msg["From"] = f"{COMPANY_NAME} <noreply@airobohub.com>"\
    msg["From"] = f"{COMPANY_NAME} <{os.getenv('MAIL_FROM')}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(html, "html"))

    
    
    server = smtplib.SMTP(MAIL_HOST, int(MAIL_PORT))
    server.starttls()
    server.login(MAIL_USERNAME, MAIL_PASSWORD)

    server.send_message(msg)
    server.quit()
