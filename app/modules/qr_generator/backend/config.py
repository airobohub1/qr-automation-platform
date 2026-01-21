from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

# load_dotenv()
load_dotenv(dotenv_path=ENV_PATH)


APP_NAME = os.getenv("APP_NAME")
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL")
STREAMLIT_BASE_URL = os.getenv("STREAMLIT_BASE_URL")

if not FASTAPI_BASE_URL or not STREAMLIT_BASE_URL:
    raise Exception("FASTAPI_BASE_URL or STREAMLIT_BASE_URL missing in .env")


SESSION_SECRET = os.getenv("SESSION_SECRET")

MAIL_HOST = os.getenv("MAIL_HOST")
MAIL_PORT = os.getenv("MAIL_PORT")
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

FREE_PLAN_LIMIT = os.getenv("FREE_PLAN_LIMIT")
PRO_PLAN_LIMIT = os.getenv("PRO_PLAN_LIMIT")
COMPANY_NAME = os.getenv("COMPANY_NAME")
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL")
SUPPORT_MOBILE = os.getenv("SUPPORT_MOBILE")
FREE_PLAN_DAILY_LIMIT = int(os.getenv("FREE_PLAN_DAILY_LIMIT", "10"))
FREE_PLAN_TOTAL_LIMIT = int(os.getenv("FREE_PLAN_TOTAL_LIMIT", "100"))

DEV_USER_ID = int(os.getenv("DEV_USER_ID", "0"))    
APP_SECRET_KEY = os.getenv("APP_SECRET_KEY")




# we should remove after testing
