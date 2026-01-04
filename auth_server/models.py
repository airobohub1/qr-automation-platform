from sqlalchemy import Column, Integer, String, Boolean, Text
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    mobile = Column(String)
    location = Column(String)
    business_info = Column(Text)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    verified = Column(Boolean, default=False)
    reset_code = Column(String, nullable=True)
