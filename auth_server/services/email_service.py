import smtplib
from email.mime.text import MIMEText
from auth_server.config import MAIL_HOST, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD, FASTAPI_BASE_URL

def send_activation_email(to_email, token):

    if not MAIL_USERNAME or not MAIL_PASSWORD:
        print("MAIL CONFIG MISSING")
        return

    activation_link = f"{FASTAPI_BASE_URL}/verify?token={token}"

    body = f"""
Welcome to AI ROBO HUB – QR Automation Platform

Please activate your account using the link below:
{activation_link}
"""

    msg = MIMEText(body)
    msg["Subject"] = "Activate your AI ROBO HUB QR Automation Account"
    msg["From"] = f"AI ROBO HUB – QR Automation Platform <{MAIL_USERNAME}>"
    msg["To"] = to_email


    try:
        server = smtplib.SMTP(MAIL_HOST, MAIL_PORT, timeout=20)
        server.set_debuglevel(1)     # TEMP DEBUG
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.sendmail(MAIL_USERNAME, [to_email], msg.as_string())
        server.quit()
        print("MAIL SENT TO", to_email)
    except Exception as e:
        print("EMAIL ERROR:", e)
