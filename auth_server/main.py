from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from auth_server.database import SessionLocal, Base, engine
from auth_server.models import User
import os

from auth_server.security import validate_password, hash_password


Base.metadata.create_all(bind=engine)

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

import traceback
from fastapi.responses import PlainTextResponse

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return PlainTextResponse("EXCEPTION:\n" + "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)), status_code=500)



# Simple ping endpoint to check if server is running
@app.get("/ping")
def ping():
    return {"status": "ok"}

# Login page - get - login
@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Login endpoint - post - login
from auth_server.security import verify_password

@app.post("/login")
def login(request: Request, email: str = Form(None), password: str = Form(None)):
    if not email or not password:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Email and password are required"
        })

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()

        if not user or not verify_password(password, user.password):
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": "Invalid email or password"
            })

        return RedirectResponse("http://localhost:8501", status_code=302)
    finally:
        db.close()
# End of login endpoint - post - login

# Registration page - get - register
@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Registration endpoint - post - register
@app.post("/register")
def register(
    request: Request,
    name: str = Form(""),
    mobile: str = Form(""),
    email: str = Form(""),
    location: str = Form(""),
    business_info: str = Form(""),
    password: str = Form("")
):
    if not all([name, mobile, email, location, password]):
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "All fields except Business Info are mandatory",
            "name": name,
            "mobile": mobile,
            "email": email,
            "location": location,
            "business_info": business_info
        })

    pwd_error = validate_password(password)
    if pwd_error:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": pwd_error,
            "name": name,
            "mobile": mobile,
            "email": email,
            "location": location,
            "business_info": business_info
        })

    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == email).first():
            return templates.TemplateResponse("register.html", {
                "request": request,
                "error": "Email already registered",
                "name": name,
                "mobile": mobile,
                "email": email,
                "location": location,
                "business_info": business_info
            })

        user = User(
            name=name,
            mobile=mobile,
            location=location,
            business_info=business_info,
            email=email,
            password=hash_password(password)
        )
        db.add(user)
        db.commit()
        return RedirectResponse("/login", status_code=302)
    finally:
        db.close()

