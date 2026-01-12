# from fastapi import Header, Depends, HTTPException, Request
# from fastapi.templating import Jinja2Templates
# from sqlalchemy.orm import Session
# from auth_server.database import SessionLocal
# from auth_server.models import User
# # from auth_server.security import verify_session_token

# import os
# from dotenv import load_dotenv
# load_dotenv()

# templates = Jinja2Templates(directory="templates")

# import hashlib
# from itsdangerous import URLSafeTimedSerializer
# from fastapi import HTTPException

# APP_SECRET_KEY = os.getenv("APP_SECRET_KEY")
# if not APP_SECRET_KEY:
#     raise Exception("APP_SECRET_KEY missing in .env")

# serializer = URLSafeTimedSerializer(APP_SECRET_KEY)

# def hash_password(password: str) -> str:
#     return hashlib.sha256(password.encode()).hexdigest()

# def verify_password(password: str, stored_hash: str) -> bool:
#     return hashlib.sha256(password.encode()).hexdigest() == stored_hash

# def generate_session_token(user_id: int) -> str:
#     return serializer.dumps({"uid": user_id})

# def verify_session_token(token: str):
#     data = serializer.loads(token, max_age=86400)
#     return data["uid"]


# # def decode_session_token(token: str):
# #     data = serializer.loads(token, max_age=86400)
# #     return data["uid"]

# # # Admin Guard - Restrict access to admin users only

# # def admin_guard(user):
# #     if user.role != "admin":
# #         raise HTTPException(status_code=403, detail="Admin access only")

# def admin_guard(request: Request, db: Session):
#     token = request.cookies.get("qr_session")
#     if not token:
#         return RedirectResponse("/login?next=/admin", status_code=302)

#     user_id = verify_session_token(token)
#     user = db.query(User).filter(User.id == user_id).first()

#     if not user or user.role != "admin":
#         return templates.TemplateResponse("login.html", {
#             "request": request,
#             "msg": "❌ Admin access required",
#             "next": "/admin"
#         })



# from fastapi import Request, HTTPException, Depends
# from fastapi.responses import RedirectResponse, HTMLResponse


# # def admin_guard(request: Request):
# #     user = request.session.get("user")

# #     if not user:
# #         return RedirectResponse("/login?next=/admin", status_code=302)

# #     if user.get("role") != "admin":
# #         return HTMLResponse("""
# #         <html>
# #         <head>
# #             <title>Access Denied</title>
# #             <style>
# #                 body{font-family:Segoe UI;text-align:center;padding-top:80px;background:#f6f7fb;}
# #                 .card{background:white;padding:40px;border-radius:12px;
# #                       box-shadow:0 0 25px rgba(0,0,0,.1);display:inline-block}
# #                 a{color:#0d6efd;text-decoration:none;font-weight:600}
# #             </style>
# #         </head>
# #         <body>
# #             <div class="card">
# #                 <h2>🚫 Admin Access Only</h2>
# #                 <p>Your account does not have admin privileges.</p>
# #                 <a href="/login">Login with Admin Account</a>
# #             </div>
# #         </body>
# #         </html>
# #         """, status_code=403)

# #     return user


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # def admin_required(
# #     authorization: str = Header(...),
# #     db: Session = Depends(get_db)
# #     ):
# #     try:
# #         user_id = verify_session_token(authorization)
# #     except:
# #         raise HTTPException(status_code=401, detail="Invalid session")

# #     user = db.query(User).filter(User.id == user_id).first()
# #     if not user or user.role != "admin":
# #         raise HTTPException(status_code=403, detail="Admin access required")

# #     return user

# from fastapi import Cookie, HTTPException
# from sqlalchemy.orm import Session
# from auth_server.database import SessionLocal
# from auth_server.models import User
# from auth_server.security import verify_session_token

# def admin_required(qr_session: str = Cookie(None)):
#     if not qr_session:
#         raise HTTPException(302, headers={"Location": "/login?next=/admin"})

#     try:
#         user_id = verify_session_token(qr_session)
#     except:
#         raise HTTPException(302, headers={"Location": "/login?next=/admin"})

#     db = SessionLocal()
#     user = db.query(User).filter(User.id == user_id).first()
#     db.close()

#     if not user or user.role != "admin":
#         raise HTTPException(403, "Admin access required")

#     return user


import os, hashlib
from dotenv import load_dotenv
from itsdangerous import URLSafeTimedSerializer

from fastapi import Cookie, HTTPException
from auth_server.database import SessionLocal
from auth_server.models import User

load_dotenv()

APP_SECRET_KEY = os.getenv("APP_SECRET_KEY")
if not APP_SECRET_KEY:
    raise Exception("APP_SECRET_KEY missing in .env")

serializer = URLSafeTimedSerializer(APP_SECRET_KEY)

# ---------------- PASSWORD UTILS ----------------

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, stored_hash: str) -> bool:
    return hashlib.sha256(password.encode()).hexdigest() == stored_hash

# ---------------- SESSION TOKEN ----------------

def generate_session_token(user_id: int) -> str:
    return serializer.dumps({"uid": user_id})

def verify_session_token(token: str) -> int:
    data = serializer.loads(token, max_age=86400)
    return data["uid"]

# ---------------- ADMIN GUARD ----------------

def admin_required(qr_session: str = Cookie(None)):
    if not qr_session:
        raise HTTPException(302, headers={"Location": "/login?next=/admin"})

    try:
        user_id = verify_session_token(qr_session)
    except:
        raise HTTPException(302, headers={"Location": "/login?next=/admin"})

    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    db.close()

    if not user or user.role != "admin":
        raise HTTPException(403, "Admin access required")

    return user

