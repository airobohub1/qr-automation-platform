import os, hashlib
from dotenv import load_dotenv
from itsdangerous import URLSafeTimedSerializer

from fastapi import Cookie, HTTPException
# from auth_server.database import SessionLocal
from app.modules.qr_generator.backend.database import SessionLocal

# from auth_server.models import User
from app.modules.qr_generator.backend.models import User


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
        raise HTTPException(status_code=401, detail="LOGIN_REQUIRED")

    try:
        user_id = verify_session_token(qr_session)
    except:
        raise HTTPException(status_code=401, detail="LOGIN_REQUIRED")

    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    db.close()

    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="NOT_ADMIN")

    return user


#------------------------------------------
