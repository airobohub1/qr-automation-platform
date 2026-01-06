from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from datetime import datetime
from uuid import uuid4
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from auth_server.database import SessionLocal, Base, engine
from auth_server.models import User, UsageStats, UserPlanDetails
from auth_server.security import hash_password, verify_password
import os

from auth_server.services.email_service import send_activation_email
from starlette.middleware.sessions import SessionMiddleware
from auth_server.config import STREAMLIT_BASE_URL


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="super-secret-key-change-this")

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

# HOME ENDPOINT
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})
# End of HOME ENDPOINT

# Login page - get & post - login

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid email or password"
        })

    if user.verified == 0:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Please activate your account from your email"
        })

    request.session["user_id"] = user.id
    # return RedirectResponse("/dashboard", status_code=302)
    # return RedirectResponse(f"http://localhost:8501?user_id={user.id}", status_code=302)
    return RedirectResponse(f"{STREAMLIT_BASE_URL}?user_id={user.id}", status_code=302)


# Login endpoint -get and post - login

# Registration page - get - register

@app.get("/register")
def register_page(request: Request, plan: str = "free"):
    return templates.TemplateResponse("register.html", {
        "request": request,
        "plan": plan
    })



# END OF Registration page - get - register


# Registration endpoint - post - register

from datetime import datetime, timedelta
from uuid import uuid4

# @app.post("/register")
# def register(
#     request: Request,
#     name: str = Form(...),
#     mobile: str = Form(...),
#     location: str = Form(...),
#     business_info: str = Form(""),
#     email: str = Form(...),
#     password: str = Form(...),
#     plan: str = Form(...),
#     db: Session = Depends(get_db)
# ):

#     # Check existing user
#     if db.query(User).filter(User.email==email).first():
#         return templates.TemplateResponse("register.html", {
#             "request":request,
#             "error":"Account already exists",
#             "plan":plan
#         })

#     # Hash password
#     hashed_pwd = hash_password(password)

#     # Subscription setup
#     today = datetime.today()
#     expiry = today + timedelta(days=30)

#     payment_status = "NA" if plan=="free" else "PENDING"

#     verify_token = str(uuid4())

#     user = User(
#         name=name,
#         mobile=mobile,
#         location=location,
#         business_info=business_info,
#         email=email,
#         password=hashed_pwd,
#         verified=0,
#         verify_token=verify_token,
#         reset_code=None,
#         plan=plan,
#         # payment_status=payment_status,

#         plan_start=today.strftime("%Y-%m-%d"),
#         plan_expiry=expiry.strftime("%Y-%m-%d"),
#         created_at=today.strftime("%Y-%m-%d %H:%M:%S")
#     )
#     payment_status = "NA" if plan=="free" else "PENDING"

#     db.add(user)
#     db.commit()

#     send_activation_email(email, verify_token)

#     return templates.TemplateResponse("login.html", {
#         "request":request,
#         "success":"Account created. Please activate from your email."
#     })


@app.post("/register")
def register(
    request: Request,
    name: str = Form(...),
    mobile: str = Form(...),
    location: str = Form(...),
    business_info: str = Form(""),
    email: str = Form(...),
    password: str = Form(...),
    plan: str = Form(...),
    db: Session = Depends(get_db)
):

    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Account already exists",
            "plan": plan
        })

    hashed_pwd = hash_password(password)
    today = datetime.utcnow()
    verify_token = str(uuid4())

    user = User(
        name=name,
        mobile=mobile,
        location=location,
        business_info=business_info,
        email=email,
        password=hashed_pwd,
        verified=0,
        verify_token=verify_token,
        reset_code=None,
        plan=plan,                # still keeping for backward compatibility
        plan_start=today,
        plan_expiry=None,
        created_at=today
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # 🔹 INSERT FREE PLAN INTO user_plan_details
    free_plan = UserPlanDetails(
        user_id=user.id,
        plan_type="free",
        amount=0,
        payment_status="success",
        plan_start=today,
        plan_expiry=None,
        is_active=1
    )

    db.add(free_plan)

    # 🔹 CREATE usage_stats ROW
    usage = UsageStats(
        user_id=user.id,
        date=today.date(),
        qr_generated_today=0,
        qr_generated_total=0,
        limit_allowed=10
    )

    db.add(usage)
    db.commit()

    send_activation_email(email, verify_token)

    return templates.TemplateResponse("check_email.html", {
        "request": request,
        "email": email
    })


# end of Registration endpoint - post - register

# Email verification endpoint

# @app.get("/verify")
# def verify(token: str, request: Request, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.verify_token==token).first()

#     if not user:
#         return templates.TemplateResponse("login.html", {
#             "request":request,
#             "error":"Invalid or expired activation link"
#         })

#     user.verified = 1
#     user.verify_token = None
#     db.commit()

#     return templates.TemplateResponse("login.html", {
#         "request":request,
#         "success":"Your account has been activated. Please login."
#     })

@app.get("/verify")
def verify_user(token: str, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verify_token == token).first()

    if not user:
        return HTMLResponse("Invalid or expired verification link")

    user.verified = 1
    db.commit()

    return templates.TemplateResponse("login.html", {
        "request": request,
        "success": "Account activated successfully. Please login now."
    })


# dashboard endpoint
@app.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse("/login", status_code=302)

    user = db.query(User).filter(User.id == user_id).first()
    plan = db.query(UserPlanDetails).filter_by(user_id=user.id, is_active=1).first()
    usage = db.query(UsageStats).filter_by(user_id=user.id).first()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "plan": plan,
        "usage": usage
    })

# end of dashboard endpoint


