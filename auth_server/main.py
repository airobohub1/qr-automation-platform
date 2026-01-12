from fastapi import FastAPI, Request, Response, Form, Depends, HTTPException, Header
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from datetime import datetime,date
from uuid import uuid4
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from auth_server.database import SessionLocal, Base, engine
from auth_server.models import User, UsageStats, UserPlanDetails, Lead, PlanMaster
from auth_server.security import hash_password, verify_password, admin_required
import os

from auth_server.services.email_service import send_activation_email
# from starlette.middleware.sessions import SessionMiddleware
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
# app.add_middleware(SessionMiddleware, secret_key="super-secret-key-change-this")

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

# @app.get("/login")
# def login_page(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request})

@app.get("/login")
def login_page(request: Request, next: str = "/qr"):
    return templates.TemplateResponse("login.html", {
        "request": request,
        "next": next
    })


from auth_server.security import generate_session_token

from fastapi import Request, Form, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from auth_server.security import generate_session_token


from fastapi.responses import RedirectResponse
from urllib.parse import quote


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
            "msg": "❌ Invalid email or password"
        })

    if not user.verified:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "msg": "❌ Please activate your account from email",
            "resend": True,
            "email": email
        })

    token = generate_session_token(user.id)

    response = RedirectResponse("http://127.0.0.1:8501", status_code=302)

    response.set_cookie(
        key="qr_session",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/"
    )

    return response




# LOGOUT ENDPOINT

@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie(
        key="qr_session",
        path="/"
    )
    return response



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
    "request": request,
    "datetime":datetime
    })


# dashboard endpoint
# @app.get("/dashboard")
# def dashboard(request: Request, db: Session = Depends(get_db)):
#     user_id = request.session.get("user_id")

#     if not user_id:
#         return RedirectResponse("/login", status_code=302)

#     user = db.query(User).filter(User.id == user_id).first()
#     plan = db.query(UserPlanDetails).filter_by(user_id=user.id, is_active=1).first()
#     usage = db.query(UsageStats).filter_by(user_id=user.id).first()

#     return templates.TemplateResponse("dashboard.html", {
#         "request": request,
#         "user": user,
#         "plan": plan,
#         "usage": usage
#     })

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
    
    plan = db.query(UserPlanDetails)\
        .filter_by(user_id=user_id, is_active=1).first()

    if not plan:
        raise HTTPException(403,"Subscription expired. Please renew.")


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

# from auth_server.security import decode_session_token, serializer


# from fastapi import Cookie

from auth_server.security import verify_session_token

from fastapi import Cookie

@app.get("/api/validate-session")
def validate_session(qr_session: str = Cookie(None), db: Session = Depends(get_db)):
    if not qr_session:
        raise HTTPException(401)

    try:
        user_id = verify_session_token(qr_session)
    except:
        raise HTTPException(401)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(401)

    return {
        "id": user.id,
        "name": user.name,
        "business_name": user.business_name,
        "plan": user.plan
    }


# @app.get("/api/validate-session")
# def validate_session(qr_session: str = Cookie(None), db: Session = Depends(get_db)):
#     if not qr_session:
#         raise HTTPException(401)

#     try:
#         user_id = verify_session_token(qr_session)
#     except:
#         raise HTTPException(401)

#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise HTTPException(401)

#     return {
#         "id": user.id,
#         "name": user.name,
#         "business_name": user.business_name,
#         "plan": user.plan
#     }


# @app.get("/api/validate-session")
# def validate_session(authorization: str = Header(None), db: Session = Depends(get_db)):
#     if not authorization:
#         raise HTTPException(401)

#     try:
#         user_id = verify_session_token(authorization)
#     except:
#         raise HTTPException(401)

#     user = db.query(User).filter(User.id==user_id).first()
#     if not user:
#         raise HTTPException(401)

#     return {
#         "id": user.id,
#         "name": user.name,
#         "business_name": user.business_name,
#         "plan": user.plan
#     }




# -----------------------------FAQ PAGE ENDPOINTS -----------------------------

@app.get("/faq")
def faq_page(request: Request):
    return templates.TemplateResponse("faq.html", {"request": request})


# -----------------------------ADMIN PANEL  -----------------------------
# -----------------------------ADMIN PANEL  -----------------------------

# Admin home endpoint

from fastapi import Depends
# from auth_server.security import admin_guard


# @app.get("/admin")
# def admin_home(request: Request, db:Session=Depends(get_db)):
#     return templates.TemplateResponse("admin_dashboard.html", {"request":request})

# @app.get("/admin", dependencies=[Depends(admin_guard)])
# def admin_home(request: Request, db:Session=Depends(get_db)):
#     return templates.TemplateResponse("admin_dashboard.html", {"request":request})

# @app.get("/admin")
# def admin_home(request: Request):
#     guard = admin_guard(request)
#     if isinstance(guard, (RedirectResponse, HTMLResponse)):
#         return guard

#     return templates.TemplateResponse("admin_dashboard.html", {"request": request})


# @app.get("/admin")
# def admin_home(request: Request, db: Session = Depends(get_db)):
#     guard = admin_guard(request, db)
#     if guard: return guard
#     return templates.TemplateResponse("admin_dashboard.html", {"request": request})

@app.get("/admin")
def admin_home(request: Request, admin=Depends(admin_required)):
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})


# LEADS WORK LSIT - ENDPOINT
# def admin_leads(request: Request, db: Session = Depends(get_db),  dependencies=[Depends(admin_guard)]):
#     leads = db.query(Lead).all()
#     return templates.TemplateResponse("admin_leads.html", {
#         "request": request,
#         "leads": leads
#     })

# @app.get("/admin/leads")
# def admin_leads(request: Request, db: Session = Depends(get_db)):
#     # guard = admin_guard(request)
#     # if isinstance(guard, (RedirectResponse, HTMLResponse)):
#     #     return guard

#     leads = db.query(Lead).all()
#     return templates.TemplateResponse("admin_leads.html", {
#         "request": request,
#         "leads": leads
#     })

@app.get("/admin/leads")
def admin_leads(request: Request, admin=Depends(admin_required), db: Session = Depends(get_db)):
    leads = db.query(Lead).all()
    return templates.TemplateResponse("admin_leads.html", {
        "request": request,
        "leads": leads
    })


# convert lead to user endpoint
@app.get("/admin/convert/{lead_id}")
def convert_lead(lead_id:int, db:Session=Depends(get_db)):
    lead=db.query(Lead).get(lead_id)
    user=db.query(User).filter(User.email==lead.email).first()
    if user:
        user.plan=lead.plan
        user.is_active=True
        db.commit()
    return RedirectResponse("/admin/leads",status_code=302)

# users work list - endpoint

from fastapi import Request, Depends
from auth_server.security import admin_required

@app.get("/admin/users")
def admin_users(
    request: Request,
    admin = Depends(admin_required),
    db: Session = Depends(get_db)
):
    users = db.query(User).all()

    return templates.TemplateResponse("admin_users.html", {
        "request": request,
        "users": users,
        "admin": admin
    })


# Enable disable user account endpoint
@app.get("/admin/toggle/{user_id}")
def toggle_user(user_id:int, db:Session=Depends(get_db)):
    u=db.query(User).get(user_id)
    u.is_active=not u.is_active
    db.commit()
    return RedirectResponse("/admin/users",status_code=302)



# Convert lead to user - post endpoint  
from fastapi import Form

@app.post("/admin/convert-lead")
def convert_lead(
    lead_id: int = Form(...),
    plan: str = Form(...),
    db: Session = Depends(get_db)
):
    lead = db.query(Lead).filter(Lead.id==lead_id).first()
    if not lead:
        raise HTTPException(404)

    # Create User
    user = User(
        name=lead.name,
        business_name=lead.business_name,
        mobile=lead.mobile,
        email=lead.email,
        password=hash_password("Welcome@123"),
        verified=1,
        plan=plan,
        created_at=datetime.utcnow()
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Activate Plan
    db.add(UserPlanDetails(
        user_id=user.id,
        plan_type=plan,
        amount=4999 if plan=="paid" else 19999,
        payment_status="success",
        plan_start=datetime.utcnow(),
        plan_expiry=datetime.utcnow()+timedelta(days=365),
        is_active=1
    ))

    send_activation_email(user.email, user.name, "welcome")

    # Delete lead
    db.delete(lead)
    db.commit()

    return RedirectResponse("/admin/leads", status_code=302)


# CRON LIKE JOB AT STARTUP

from threading import Thread
import time

def expiry_watcher():
    while True:
        db = SessionLocal()
        today = datetime.utcnow()

        plans = db.query(UserPlanDetails)\
            .filter(UserPlanDetails.plan_expiry!=None,
                    UserPlanDetails.plan_expiry < today,
                    UserPlanDetails.is_active==1).all()

        for p in plans:
            user = db.query(User).get(p.user_id)
            p.is_active = 0
            user.plan = "free"
            send_activation_email(user.email, user.name, "expired")

        db.commit()
        db.close()
        time.sleep(3600)  # every hour


# register watcher at startup
@app.on_event("startup")
def start_expiry_engine():
    Thread(target=expiry_watcher, daemon=True).start()



@app.post("/admin/renew")
def admin_renew(admin=Depends(admin_required), user_id: int = Form(...), db: Session = Depends(get_db)):

    plan = db.query(UserPlanDetails).filter_by(user_id=user_id).first()

    if not plan:
        raise HTTPException(404, "Plan not found")

    plan.plan_expiry = datetime.utcnow() + timedelta(days=365)
    plan.is_active = 1

    user = db.query(User).get(user_id)
    user.plan = "paid"

    db.commit()

    return RedirectResponse("/admin/users", status_code=302)


