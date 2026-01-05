from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, Float, ForeignKey
from sqlalchemy import Date
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Profile
    name = Column(String)
    mobile = Column(String)
    location = Column(String)
    business_info = Column(String)

    # Auth
    email = Column(String, unique=True, index=True)
    password = Column(String)

    verified = Column(Integer, default=0)
    verify_token = Column(String)
    reset_code = Column(String)

    # Subscription
    plan = Column(String, default="FREE")         # FREE / PRO / ENTERPRISE
    payment_status = Column(String, default="NA") # NA / PENDING / PAID
    plan_start = Column(String)
    plan_expiry = Column(String)

    # Audit
    created_at = Column(String)


class UserPlanDetails(Base):
    __tablename__ = "user_plan_details"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    plan_type = Column(String)
    amount = Column(Float, default=0)
    currency = Column(String, default="INR")
    payment_status = Column(String, default="success")
    plan_start = Column(DateTime)
    plan_expiry = Column(DateTime, nullable=True)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)


class UsageStats(Base):
    __tablename__ = "usage_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date)
    qr_generated_today = Column(Integer, default=0)
    qr_generated_total = Column(Integer, default=0)
    limit_allowed = Column(Integer, default=10)
