from fastapi import FastAPI, Request, Response, Form, Depends, HTTPException, Cookie
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from datetime import datetime,date
from uuid import uuid4
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from auth_server.database import SessionLocal, Base, engine
from auth_server.models import User, UsageStats, UserPlanDetails, Lead, PlanMaster
from auth_server.security import hash_password, verify_password
import os

from auth_server.services.email_service import send_activation_email
from starlette.middleware.sessions import SessionMiddleware
from auth_server.config import STREAMLIT_BASE_URL
from auth_server.models import QRUsageEvent, Plan
from auth_server.config import FREE_PLAN_LIMIT
from sqlalchemy import text,func


from uuid import uuid4
from datetime import datetime, timedelta

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

from auth_server.security import generate_session_token

from fastapi import Request, Form, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from auth_server.security import generate_session_token

@app.post("/login")
def login(request: Request,
          email: str = Form(...),
          password: str = Form(...),
          db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "msg": "Invalid email or password"
        })

    if not user.verified:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "msg": "Please activate your account from email",
            "resend": True,
            "email": email
        })

    token = generate_session_token(user.id)

    response = RedirectResponse(url="http://127.0.0.1:8501", status_code=302)

    response.set_cookie(
        key="qr_session",
        value=token,
        httponly=True,
        samesite="lax",
        path="/"
    )

    return response


# @app.post("/login")
# def login(
#     request: Request,
#     email: str = Form(...),
#     password: str = Form(...),
#     db: Session = Depends(get_db)
# ):
#     user = db.query(User).filter(User.email == email).first()

#     if not user or not verify_password(password, user.password):
#         return templates.TemplateResponse("login.html", {
#             "request": request,
#             "msg": "Invalid email or password"
#         })

#     if not user.verified:
#         return templates.TemplateResponse("login.html", {
#             "request": request,
#             "msg": "Please activate your account from your email"
#         })

#     session_token = generate_session_token(user.id)

#     response = RedirectResponse(
#         url="http://127.0.0.1:8501",
#         status_code=302
#     )

#     # response.set_cookie(
#     #     key="qr_session",
#     #     value=session_token,
#     #     httponly=True,
#     #     samesite="lax",
#     #     path="/"
#     # )

#     response.set_cookie(
#         key="qr_session",
#         value=session_token,
#         httponly=True,
#         samesite="lax",
#         secure=False,
#         domain="127.0.0.1",
#         path="/"
#     )

#     return response



# @app.post("/login")
# def login_user(
#     response: Response,
#     request: Request,
#     email: str = Form(...),
#     password: str = Form(...),
#     db: Session = Depends(get_db)
# ):
#     user = db.query(User).filter(User.email == email).first()
#     if not user or not verify_password(password, user.password):
#         return templates.TemplateResponse("login.html", {
#             "request": request,
#             "error": "Invalid credentials"
#         })

#     if not user.verified:
#         return templates.TemplateResponse("login.html", {
#             "request": request,
#             "error": "Please activate your account from email"
#         })

#     session_token = generate_session_token(user.id)

#     resp = RedirectResponse(
#         url=os.getenv("STREAMLIT_BASE_URL"),
#         status_code=302
#     )

#     resp.set_cookie(
#         key="qr_session",
#         value=session_token,
#         httponly=True,
#         max_age=86400,
#         samesite="lax"
#     )

#     return resp



# @app.post("/login")
# def login_user(
#     request: Request,
#     email: str = Form(...),
#     password: str = Form(...),
#     db: Session = Depends(get_db)
# ):
#     user = db.query(User).filter(User.email == email).first()

#     if not user or not verify_password(password, user.password):
#         return templates.TemplateResponse("login.html", {
#             "request": request,
#             "error": "Invalid email or password"
#         })

#     # if user.verified == 0:
#     #     return templates.TemplateResponse("login.html", {
#     #         "request": request,
#     #         "error": "Please activate your account from your email"
#     #     })

#     if not user.verified:
#         return templates.TemplateResponse("login.html", {
#             "request": request,
#             "error": "Account not activated. Please activate your account from email.",
#             "resend": True,
#             "email": email
#     })


#     # Successful login
#     # request.session["user_id"] = user.id
#     # # return RedirectResponse("/dashboard", status_code=302)
#     # # return RedirectResponse(f"http://localhost:8501?user_id={user.id}", status_code=302)
#     # return RedirectResponse(f"{STREAMLIT_BASE_URL}?user_id={user.id}", status_code=302)

#     from auth_server.security import generate_session_token

#     token = generate_session_token(user.id)

#     response = RedirectResponse(
#             url=f"{STREAMLIT_BASE_URL}",
#             status_code=302
#         )
#     response.set_cookie(
#             key="qr_session",
#             value=token,
#             httponly=True,
#             secure=False,
#             samesite="lax"
#         )
#     return response


# LOGOUT ENDPOINT

@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("qr_session", path="/", domain="127.0.0.1")
    return response

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



@app.post("/register")
def register(
    request: Request,
    name: str = Form(...),
    business_name: str = Form(...),
    mobile: str = Form(...),
    location: str = Form(...),
    business_info: str = Form(""),
    email: str = Form(...),
    password: str = Form(...),
    plan: str = Form(...),
    db: Session = Depends(get_db)
):

    if db.query(User).filter(User.email == email).first():
        # return templates.TemplateResponse("register.html", {
        #     "request": request,
        #     "error": "Account already exists",
        #     "plan": plan
        return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "You already registered but your account is not activated.",
        "resend": True,
        "email": email
        })

    hashed_pwd = hash_password(password)
    today = datetime.utcnow()
    verify_token = str(uuid4())
    token_expiry = datetime.utcnow() + timedelta(minutes=30)

    user = User(
        name=name,
        business_name=business_name,
        mobile=mobile,
        location=location,
        business_info=business_info,
        email=email,
        password=hashed_pwd,
        token_expiry=token_expiry,
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

    send_activation_email(email, user.name, verify_token)

    return templates.TemplateResponse("check_email.html", {
        "request": request,
        "email": email
    })


# end of Registration endpoint - post - register



@app.get("/verify")
def verify_user(token: str, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verify_token == token).first()

    if not user:
        return HTMLResponse("Invalid or expired verification link")


    if user.token_expiry < datetime.utcnow():
        return templates.TemplateResponse("activation_expired.html", {
            "request": request,
            "email": user.email
        })

    user.verified = 1
    db.commit()

    # return templates.TemplateResponse("login.html", {
    #     "request": request,
    #     "success": "Account activated successfully. Please login now."
    return templates.TemplateResponse("activation_success.html", {
    "request": request
    
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

# API to get user profile
# this is to display user info in streamlit app / QR dashboard
@app.get("/api/user-profile/{user_id}")
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id==user_id).first()
    return {
        "name": user.name,
        "business": user.business_info
    }

# end of API to get user profile


# End point for QR COde generation log for usage tracking and also for audit trail
# insert qr usage event

@app.post("/api/log-usage/{user_id}")
def log_usage(user_id: int, event_type: str = Form(...), count: int = Form(...), db: Session = Depends(get_db)):
    usage = QRUsageEvent(user_id=user_id, event_type=event_type, count=count)
    db.add(usage)
    db.commit()
    return {"status":"logged"}
# End point for QR COde limit usage update



# Fetch live usage for validation in streamlit app
# @app.get("/api/usage/{user_id}")
# def get_usage(user_id: int, db: Session = Depends(get_db)):
#     today = datetime.utcnow().date()
#     used = db.query(func.sum(QRUsageEvent.count)) \
#              .filter(QRUsageEvent.user_id==user_id,
#                      QRUsageEvent.status=="unbilled",
#                      QRUsageEvent.created_at >= today).scalar() or 0
#     return {"used": used, "limit": FREE_PLAN_LIMIT}

from sqlalchemy import func
from auth_server.models import QRUsageEvent

# @app.get("/api/usage/{user_id}")
# def get_usage(user_id: int, db: Session = Depends(get_db)):
#     today = datetime.utcnow().date()

#     used = db.query(func.sum(QRUsageEvent.count)) \
#         .filter(
#             QRUsageEvent.user_id == user_id,
#             QRUsageEvent.status == "unbilled",
#             QRUsageEvent.created_at >= today
#         ).scalar() or 0

#     return {"used": int(used)}

@app.get("/api/usage/{user_id}")
def get_usage(user_id:int, db:Session=Depends(get_db)):
    today = datetime.utcnow().date()

    today_used = db.query(func.sum(QRUsageEvent.count))\
        .filter(QRUsageEvent.user_id==user_id,
                func.date(QRUsageEvent.created_at)==today).scalar() or 0

    total = db.query(func.sum(QRUsageEvent.count))\
        .filter(QRUsageEvent.user_id==user_id).scalar() or 0

    plan = db.query(PlanMaster).filter(PlanMaster.plan_name=="free").first()

    return {
        "today": int(today_used),
        "total": int(total),
        "remaining": max(plan.total_limit-total,0)
    }


#  fetch user detaisl for qr dashboard

@app.get("/api/user/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    return {
        "name": user.name,
        "business_name": user.business_name,
        "business_info": user.business_info,
        "plan": user.plan
    }

# fetch user detaisl for qr dashboard
# both above one USER AND THIS PROIR ONE ARE SAME. DELETE ONE LATER
@app.get("/api/profile/{user_id}")
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    return {
        "name": user.name,
        "business_name": user.business_name,
        "business_info": user.business_info,
        "mobile": user.mobile,
        "location": user.location,
        "email": user.email,
        "plan": user.plan

    }

# Update user profile endpoint
@app.post("/api/profile/{user_id}")
def update_profile(
    user_id: int,
    name: str = Form(...),
    business_name: str = Form(...),
    business_info: str = Form(""),
    mobile: str = Form(...),
    location: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    user.name = name
    user.business_name = business_name
    user.mobile = mobile
    user.location = location
    user.business_info = business_info
    db.commit()
    return {"msg": "Profile updated successfully"}


# GET RESEND ACTIVATION PAGE

@app.get("/resend-activation")
def resend_activation_get(request: Request, email: str, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == email).first()
    if user:
        user.verify_token = str(uuid4())
        user.token_expiry = datetime.utcnow() + timedelta(minutes=30)
        db.commit()
        send_activation_email(user.email, user.verify_token, user.name)

    return templates.TemplateResponse("check_email.html", {
        "request": request,
        "email": email,
        "msg": "A new activation link has been sent to your email."
    })



# Resend Activation Endpoint
from fastapi import Request

@app.post("/resend-activation")
def resend_activation(request: Request,
                      email: str = Form(...),
                      db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == email).first()

    if user:
        user.verify_token = str(uuid4())
        user.token_expiry = datetime.utcnow() + timedelta(minutes=30)
        db.commit()
        send_activation_email(user.email, user.verify_token)

    return templates.TemplateResponse("check_email.html", {
        "request": request,
        "email": email,
        "msg": "A new activation link has been sent to your email."
    })



@app.get("/resend-activation")
def resend_page(request: Request):
    return templates.TemplateResponse("resend_activation.html", {"request": request})

@app.post("/resend-activation")
def resend_submit(request: Request, email: str = Form(...), db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == email).first()

    if not user:
        return templates.TemplateResponse("resend_activation.html", {
            "request": request,
            "error": "Account not found."
        })

    if user.verified:
        return templates.TemplateResponse("resend_activation.html", {
            "request": request,
            "error": "Account already activated. Please login."
        })

    user.verify_token = str(uuid4())
    user.token_expiry = datetime.now() + timedelta(minutes=30)
    db.commit()

    # send_activation_email(user.email, user.verify_token, user.name)
    send_activation_email(user.email, user.name, user.verify_token)

    return templates.TemplateResponse("resend_activation.html", {
        "request": request,
        "msg": "New activation link sent to your email."
    })


# Quota check endpoint

@app.get("/api/check-quota/{user_id}")
def check_quota(user_id: int, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    plan = db.query(PlanMaster).filter(PlanMaster.plan_name == user.plan).first()
    if not plan:
        raise HTTPException(500, "Plan configuration missing")

    today = datetime.utcnow().date()

    today_used = db.query(func.sum(QRUsageEvent.count)) \
        .filter(
            QRUsageEvent.user_id == user_id,
            func.date(QRUsageEvent.created_at) == today
        ).scalar() or 0

    total_used = db.query(func.sum(QRUsageEvent.count)) \
        .filter(QRUsageEvent.user_id == user_id) \
        .scalar() or 0

    return {
        "daily_remaining": max(plan.daily_limit - today_used, 0),
        "total_remaining": max(plan.total_limit - total_used, 0),
        "plan": plan.plan_name
    }



# @app.get("/api/check-quota/{user_id}")
# def check_quota(user_id: int, db: Session = Depends(get_db)):

#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise HTTPException(404, "User not found")

#     plan = db.query(PlanMaster).filter(PlanMaster.plan_name == user.plan).first()
#     if not plan:
#         raise HTTPException(500, "Plan configuration missing")

#     today = datetime.utcnow().date()

#     today_used = db.query(func.sum(QRUsageEvent.count)).filter(
#         QRUsageEvent.user_id == user_id,
#         func.date(QRUsageEvent.created_at) == today,
#         QRUsageEvent.billed == False
#     ).scalar() or 0

#     total_used = db.query(func.sum(QRUsageEvent.count)).filter(
#         QRUsageEvent.user_id == user_id,
#         QRUsageEvent.billed == False
#     ).scalar() or 0

#     return {
#         "daily_remaining": max(plan.daily_limit - today_used, 0),
#         "total_remaining": max(plan.total_limit - total_used, 0),
#         "plan": plan.plan_name
#     }

# # Endpoint for Resend Activation Page



# @app.get("/api/check-quota/{user_id}")
# def check_quota(user_id: int, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise HTTPException(404, "User not found")

#     plan = db.query(PlanMaster).filter(PlanMaster.plan_name == user.plan).first()
#     if not plan:
#         raise HTTPException(500, "Plan configuration missing")

#     today = datetime.utcnow().date()

#     today_used = db.query(func.sum(QRUsageEvent.count)).filter(
#         QRUsageEvent.user_id == user_id,
#         func.date(QRUsageEvent.created_at) == today,
#         QRUsageEvent.billed == False
#     ).scalar() or 0

#     total_used = db.query(func.sum(QRUsageEvent.count)).filter(
#         QRUsageEvent.user_id == user_id,
#         QRUsageEvent.billed == False
#     ).scalar() or 0

#     return {
#         "daily_remaining": max(plan.daily_limit - today_used, 0),
#         "total_remaining": max(plan.total_limit - total_used, 0),
#         "plan": plan.plan_name
#     }



# end of  quota check endpoint

# lead end point - get

@app.get("/lead")
def lead_page(request: Request, plan: str):
    return templates.TemplateResponse("lead.html", {
        "request": request,
        "plan": plan
    })


# end of lead end point - get

# leads end point
@app.post("/api/lead")
def save_lead(
    name: str = Form(...),
    business_name: str = Form(...),
    email: str = Form(...),
    mobile: str = Form(...),
    plan: str = Form(...),
    source: str = Form("WEB"),
    db: Session = Depends(get_db)
):
    lead = Lead(
        name=name,
        business_name=business_name,
        email=email,
        mobile=mobile,
        plan=plan,
        source=source,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    db.add(lead)
    db.commit()
    return {"msg": "Lead captured successfully"}

# end of leads end point

#  Seed plans ONCE at startup event

@app.on_event("startup")
def seed_plans():
    db = SessionLocal()
    if not db.query(PlanMaster).first():
        db.add_all([
            PlanMaster(plan_name="free", daily_limit=10, total_limit=100),
            PlanMaster(plan_name="paid", daily_limit=500, total_limit=5000),
            PlanMaster(plan_name="enterprise", daily_limit=1000, total_limit=50000),
        ])
        db.commit()
    db.close()


#  Validate Session API

from auth_server.security import decode_session_token, serializer

# @app.get("/api/validate-session")
# def validate_session(request: Request, db: Session = Depends(get_db)):
#     token = request.headers.get("Authorization")
#     if not token:
#         raise HTTPException(401)

#     try:
#         data = verify_session_token(token)
#     except:
#         raise HTTPException(401)

#     user = db.query(User).filter(User.id == data["user_id"]).first()
#     if not user:
#         raise HTTPException(401)

#     return {"id": user.id, "name": user.name, "plan": user.plan}


# @app.get("/api/validate-session")
# def validate_session(request: Request, db: Session = Depends(get_db)):
#     token = request.cookies.get("qr_session")
#     if not token:
#         raise HTTPException(status_code=401)

#     try:
#         data = serializer.loads(token, max_age=86400)
#         user = db.query(User).filter(User.id == data["uid"]).first()
#         if not user:
#             raise HTTPException(status_code=401)
#         return {"id": user.id, "name": user.name, "plan": user.plan, "business": user.business_name}
#     except:
#         raise HTTPException(status_code=401)


# @app.get("/api/validate-session")
# def validate_session(qr_session: str = Cookie(None), db: Session = Depends(get_db)):
#     if not qr_session:
#         raise HTTPException(status_code=401)

#     user_id = verify_session_token(qr_session)
#     if not user_id:
#         raise HTTPException(status_code=401)

#     user = db.query(User).get(user_id)
#     if not user:
#         raise HTTPException(status_code=401)

#     return {
#         "id": user.id,
#         "name": user.name,
#         "business_name": user.business_name,
#         "plan": user.plan
#     }

# from fastapi import Header

# @app.get("/api/validate-session")
# def validate_session(authorization: str = Header(None), db: Session = Depends(get_db)):
#     if not authorization:
#         raise HTTPException(status_code=401)

#     user_id = decode_session_token(authorization)
#     user = db.query(User).get(user_id)

#     if not user:
#         raise HTTPException(status_code=401)

#     return {
#         "id": user.id,
#         "name": user.name,
#         "business_name": user.business_name,
#         "plan": user.plan
#     }


from auth_server.security import decode_session_token
from fastapi import Cookie

# @app.get("/api/validate-session")
# def validate_session(qr_session: str = Cookie(None), db: Session = Depends(get_db)):
#     if not qr_session:
#         raise HTTPException(401)

#     user_id = decode_session_token(qr_session)
#     if not user_id:
#         raise HTTPException(401)

#     user = db.query(User).get(user_id)
#     if not user:
#         raise HTTPException(401)

#     return {
#         "id": user.id,
#         "name": user.name,
#         "business_name": user.business_name,
#         "plan": user.plan
#     }


from fastapi import Cookie

@app.get("/api/validate-session")
def validate_session(qr_session: str = Cookie(None), db: Session = Depends(get_db)):

    if not qr_session:
        raise HTTPException(status_code=401)

    try:
        user_id = decode_session_token(qr_session)
    except:
        raise HTTPException(status_code=401)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401)

    return {
        "id": user.id,
        "name": user.name,
        "business_name": user.business_name,
        "plan": user.plan
    }
