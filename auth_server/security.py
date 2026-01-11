

import os
from dotenv import load_dotenv
load_dotenv()

import hashlib
from itsdangerous import URLSafeTimedSerializer

APP_SECRET_KEY = os.getenv("APP_SECRET_KEY")
if not APP_SECRET_KEY:
    raise Exception("APP_SECRET_KEY missing in .env")

serializer = URLSafeTimedSerializer(APP_SECRET_KEY)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, stored_hash: str) -> bool:
    return hashlib.sha256(password.encode()).hexdigest() == stored_hash

def generate_session_token(user_id: int) -> str:
    return serializer.dumps({"uid": user_id})

def decode_session_token(token: str):
    data = serializer.loads(token, max_age=86400)
    return data["uid"]


# # # import re
# # from passlib.context import CryptContext
# # # from itsdangerous import URLSafeTimedSerializer
# # # import os

# # # from dotenv import load_dotenv  
# # # from itsdangerous import URLSafeTimedSerializer

# # # # FORCE .env LOAD BEFORE ANYTHING
# # # BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# # # ENV_PATH = os.path.join(BASE_DIR, ".env")
# # # load_dotenv(ENV_PATH)



# # pwd_context = CryptContext(
# #     schemes=["argon2"],
# #     deprecated="auto"
# # )

# # def validate_password(pwd: str):
# #     if not pwd:
# #         return "Password is required"
# #     if len(pwd) < 8:
# #         return "Password must be at least 8 characters"
# #     if len(pwd) > 64:
# #         return "Password must not exceed 64 characters"
# #     if not re.search(r"[A-Z]", pwd):
# #         return "Password must contain at least one uppercase letter"
# #     if not re.search(r"[a-z]", pwd):
# #         return "Password must contain at least one lowercase letter"
# #     if not re.search(r"[0-9]", pwd):
# #         return "Password must contain at least one digit"
# #     if not re.search(r"[!@#$%^&*()_+=\-{}\[\]:;\"'<>,.?/]", pwd):
# #         return "Password must contain at least one special character"
# #     return None

# # def hash_password(password: str) -> str:
# #     return pwd_context.hash(password.strip())

# # def verify_password(plain, hashed) -> bool:
# #     return pwd_context.verify(plain.strip(), hashed)


# # # # Session Token Management for QR Dashboard
# # # # from itsdangerous import URLSafeTimedSerializer
# # # # import os

# # # # APP_SECRET_KEY = os.getenv("APP_SECRET_KEY")
# # # SECRET_KEY = os.getenv("APP_SECRET_KEY")

# # # if not SECRET_KEY:
# # #     raise Exception("APP_SECRET_KEY missing in .env")

# # # serializer = URLSafeTimedSerializer(SECRET_KEY)

# # # def generate_session_token(user_id: int):
# # #     return serializer.dumps({"user_id": user_id})

# # # def verify_session_token(token: str, max_age=3600):
# # #     return serializer.loads(token, max_age=max_age)


# # # # Token is:
# # # # Cryptographically signed
# # # # Time-limited (1 hour)
# # # # Impossible to forge


# # from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
# # import os

# # APP_SECRET_KEY = os.getenv("APP_SECRET_KEY")
# # if not APP_SECRET_KEY:
# #     raise Exception("APP_SECRET_KEY missing in .env")

# # serializer = URLSafeTimedSerializer(APP_SECRET_KEY)

# # def generate_session_token(user_id: int):
# #     return serializer.dumps({"uid": user_id})

# # def decode_session_token(token: str, max_age=86400):
# #     try:
# #         data = serializer.loads(token, max_age=max_age)
# #         return data["uid"]
# #     except (BadSignature, SignatureExpired):
# #         return None

# from dotenv import load_dotenv
# load_dotenv()

# from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
# from passlib.context import CryptContext
# import os

# # ---------- PASSWORD HASHING ----------

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def hash_password(password: str):
#     return pwd_context.hash(password)

# def verify_password(password: str, hashed_password: str):
#     return pwd_context.verify(password, hashed_password)

# # ---------- SESSION TOKEN SYSTEM ----------



# APP_SECRET_KEY = os.getenv("APP_SECRET_KEY")

# if not APP_SECRET_KEY:
#     raise Exception("APP_SECRET_KEY missing in .env")

# serializer = URLSafeTimedSerializer(APP_SECRET_KEY)

# def generate_session_token(user_id: int):
#     return serializer.dumps({"uid": user_id})

# def decode_session_token(token: str, max_age=86400):
#     try:
#         data = serializer.loads(token, max_age=max_age)
#         return data["uid"]
#     except (BadSignature, SignatureExpired):
#         return None
