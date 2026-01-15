# import email
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from auth_server.config import MAIL_HOST, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD, FASTAPI_BASE_URL
# from auth_server.config import COMPANY_NAME, SUPPORT_EMAIL, SUPPORT_MOBILE

# from dotenv import load_dotenv

# load_dotenv()



# def send_activation_email(email, token, name):

#     activation_url = f"{FASTAPI_BASE_URL}/verify/{token}"

#     msg = MIMEMultipart("alternative")
#     msg["Subject"] = f"{COMPANY_NAME} – Activate your QR Automation Account"
#     msg["From"] = f"{COMPANY_NAME} <{MAIL_USERNAME}>"
#     msg["To"] = email

#     html = f"""
#     <div style="font-family:Arial;padding:20px">
#         <h2>Hi {name},</h2>
#         <p>Welcome to <b>{COMPANY_NAME} – QR Automation Platform</b>.</p>

#         <p>Your activation link is valid for <b>30 minutes</b>.</p>

#         <a href="{activation_url}" 
#         style="padding:10px 20px;background:#4f46e5;color:white;text-decoration:none;border-radius:6px;">
#         Activate My Account
#         </a>

#         <hr>
#         <p>
#         For customized QR solutions please contact our Sales Team.<br>
#         📞 {SUPPORT_MOBILE}<br>
#         ✉ {SUPPORT_EMAIL}
#         </p>
#         <p>Regards,<br><b>{COMPANY_NAME} Team</b></p>
#     </div>
#     """

#     msg.attach(MIMEText(html, "html"))

#     with smtplib.SMTP(MAIL_HOST, MAIL_PORT) as server:
#         server.starttls()
#         server.login(MAIL_USERNAME, MAIL_PASSWORD)
#         server.sendmail(MAIL_USERNAME, email, msg.as_string())


import os, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL")
SUPPORT_MOBILE = os.getenv("SUPPORT_MOBILE")
COMPANY_NAME = os.getenv("COMPANY_NAME")
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL")


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
    msg["From"] = f"{COMPANY_NAME} <{MAIL_USERNAME}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(html, "html"))

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(MAIL_USERNAME, MAIL_PASSWORD)
    server.send_message(msg)
    server.quit()




# def send_activation_email(to_email: str, name: str, token: str):
#     activation_link = f"{FASTAPI_BASE_URL}/verify?token={token}"

#     subject = f"Activate Your {COMPANY_NAME} Account"

#     html = f"""
#     <html>
#     <body style="font-family:Arial; background:#f4f6f8; padding:20px;">
#       <div style="max-width:600px; margin:auto; background:white; padding:25px; border-radius:8px;">
#         <h2 style="color:#2b5cff;">Welcome to {COMPANY_NAME} 🚀</h2>

#         <p>Hi <b>{name}</b>,</p>

#         <p>Thank you for registering with <b>{COMPANY_NAME}</b>. Please activate your account using the button below:</p>

#         <div style="text-align:center; margin:30px;">
#           <a href="{activation_link}"
#              style="background:#2b5cff; color:white; padding:12px 24px;
#              text-decoration:none; border-radius:5px;">
#              Activate My Account
#           </a>
#           <p><b>Need Help?</b></p>
#           <p>📞 {SUPPORT_MOBILE}<br>
#             📧 {SUPPORT_EMAIL}</p>

#           <p style="color:gray;font-size:12px;">
#           For customized QR automation or enterprise solutions, contact our sales team anytime.
#           </p>
#         </div>

#         <p>This link will expire in <b>30 minutes</b>.</p>

#         <hr>

#         <p style="font-size:13px; color:#666;">
#         If you face any issues, contact our support team:<br>
#         📧 {SUPPORT_EMAIL}<br>
#         📞 {SUPPORT_MOBILE}
#         </p>

#         <p style="font-size:12px; color:#999;">© {COMPANY_NAME}</p>
#       </div>
#     </body>
#     </html>
#     """

#     msg = MIMEMultipart("alternative")
#     msg["From"] = f"{COMPANY_NAME} <{MAIL_USERNAME}>"
#     msg["To"] = to_email
#     msg["Subject"] = subject
#     msg.attach(MIMEText(html, "html"))

#     server = smtplib.SMTP("smtp.gmail.com", 587)
#     server.starttls()
#     server.login(MAIL_USERNAME, MAIL_PASSWORD)
#     server.send_message(msg)
#     server.quit()
