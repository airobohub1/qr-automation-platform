import re
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

def validate_password(pwd: str):
    if not pwd:
        return "Password is required"
    if len(pwd) < 8:
        return "Password must be at least 8 characters"
    if len(pwd) > 64:
        return "Password must not exceed 64 characters"
    if not re.search(r"[A-Z]", pwd):
        return "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", pwd):
        return "Password must contain at least one lowercase letter"
    if not re.search(r"[0-9]", pwd):
        return "Password must contain at least one digit"
    if not re.search(r"[!@#$%^&*()_+=\-{}\[\]:;\"'<>,.?/]", pwd):
        return "Password must contain at least one special character"
    return None

def hash_password(password: str) -> str:
    return pwd_context.hash(password.strip())

def verify_password(plain, hashed) -> bool:
    return pwd_context.verify(plain.strip(), hashed)
