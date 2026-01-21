
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from ..models import Lead, User
from ..database import get_db

router = APIRouter()

from fastapi.templating import Jinja2Templates
import os

BASE_DIR = os.path.dirname(__file__)
templates = Jinja2Templates(
    directory=os.path.join(BASE_DIR, "../admin_ui/templates")
)



@router.get("/admin/convert/{lead_id}")
def convert_lead(
    lead_id: int,
    db: Session = Depends(get_db)
):
    lead = db.query(Lead).get(lead_id)
    if not lead:
        return RedirectResponse("/admin/leads", status_code=302)

    user = db.query(User).filter(User.email == lead.email).first()
    if user:
        user.plan = lead.plan
        user.is_active = True
        db.commit()

    return RedirectResponse("/admin/leads", status_code=302)
