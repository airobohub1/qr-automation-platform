
import streamlit as st
import requests
import os
import requests

from single_qr import single_qr_page
from bulk_qr import bulk_qr_page

from dotenv import load_dotenv
load_dotenv(dotenv_path="../.env")
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL")

st.set_page_config(page_title="AI ROBO HUB – QR Automation Platform", layout="wide")





params = st.query_params
user_id = params.get("user_id")

DEV_MODE = os.getenv("DEV_MODE", "true").lower() == "true"

if not user_id:
    if DEV_MODE:
        user_id = "DEV_USER"
        st.warning("Running in DEV MODE – authentication bypassed")
    else:
        st.error("❌ Unauthorized Access")
        st.stop()


user_profile = {}
if user_id != "DEV_USER":
    try:
        r = requests.get(f"{FASTAPI_BASE_URL}/api/user-profile/{user_id}")
        user_profile = r.json()
    except:
        user_profile = {}

from ui.ui_layout import render_layout
render_layout(user_profile)


# Session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "dashboard"

st.sidebar.title("AI ROBO HUB")
st.sidebar.markdown("### QR Automation Platform")
st.sidebar.write(f"User ID: {user_id}")

if st.sidebar.button("🏠 Dashboard"):
    st.session_state.page = "dashboard"

if st.sidebar.button("➕ Single QR Generator"):
    st.session_state.page = "single"

if st.sidebar.button("📂 Bulk QR Generator"):
    st.session_state.page = "bulk"

st.sidebar.markdown("---")
st.sidebar.button("🚪 Logout")

# -------- PAGE ROUTER -------- #

def dashboard_page():

    import requests

    try:
        usage_resp = requests.get(f"{FASTAPI_BASE_URL}/api/usage/{user_id}", timeout=5).json()
        used = usage_resp.get("used", 0)
    except Exception:
        used = 0

    try:
        profile_resp = requests.get(f"{FASTAPI_BASE_URL}/api/user/{user_id}", timeout=5).json()
        plan = profile_resp.get("plan", "FREE").upper()
        name = profile_resp.get("name", "User")
        business = profile_resp.get("business", "")
    except Exception:
        plan, name, business = "FREE", "User", ""

    st.title("📊 QR Automation Dashboard")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Today's QR Usage", used)
    with col2:
        st.metric("Plan", plan)
    with col3:
        st.metric("User", name)

    st.write("Business:", business)
    st.write("Use left menu to generate Single or Bulk QR Codes.")


# need to check wether below code is part of the above function or outside

if st.session_state.page == "dashboard":
    dashboard_page()
elif st.session_state.page == "single":
    single_qr_page(user_id)
elif st.session_state.page == "bulk":
    bulk_qr_page(user_id)



