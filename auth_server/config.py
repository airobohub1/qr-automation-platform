from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

# load_dotenv()
load_dotenv(dotenv_path=ENV_PATH)


APP_NAME = os.getenv("APP_NAME")
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL")
STREAMLIT_BASE_URL = os.getenv("STREAMLIT_BASE_URL")

SESSION_SECRET = os.getenv("SESSION_SECRET")

MAIL_HOST = os.getenv("MAIL_HOST")
MAIL_PORT = os.getenv("MAIL_PORT")
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

FREE_PLAN_LIMIT = os.getenv("FREE_PLAN_LIMIT")
PRO_PLAN_LIMIT = os.getenv("PRO_PLAN_LIMIT")

# we should remove after testing
print("ENV CHECK → MAIL_USERNAME:", MAIL_USERNAME)
print("ENV CHECK → MAIL_PASSWORD:", "SET" if MAIL_PASSWORD else "MISSING")
print("ENV CHECK → FASTAPI_BASE_URL:", FASTAPI_BASE_URL)
print("ENV CHECK → STREAMLIT_BASE_URL:", STREAMLIT_BASE_URL)