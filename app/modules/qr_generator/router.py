import streamlit as st
from dotenv import load_dotenv
from .services import validate_session
from .pages.dashboard import dashboard_page
from .pages.profile import profile_page
from .pages.single import single_qr_page
from .pages.bulk import bulk_qr_page
# from qr_dashboard.ui.ui_layout import render_layout
# from app.modules.qr_generator.pages.ui_layout import render_layout

import os

load_dotenv()
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL")

def qr_router():
    st.set_page_config(page_title="AI ROBO HUB – QR Automation Platform", layout="wide")

    if "page" not in st.session_state:
        st.session_state.page="dashboard"


    resp = validate_session(st.context.cookies)
    if resp.status_code != 200:
        st.stop()
    

    user = resp.json()
    user_id = user["id"]
    user_name = user["name"]
    business = user.get("business_name","")
    plan = user.get("plan","free")

    # render_layout({"name":user_name,"business_name":business,"plan":plan})

    st.sidebar.title("AI ROBO HUB")
    st.sidebar.markdown("### QR Automation Platform")

    st.sidebar.markdown("---")

    def nav(btn, page):
        if st.sidebar.button(btn, use_container_width=True):
            st.session_state.page = page

    nav("🏠 Dashboard", "dashboard")
    nav("➕ Single QR", "single")
    nav("📂 Bulk QR", "bulk")
    nav("👤 Profile", "profile")

    # if st.sidebar.button("🏠 Dashboard"): st.session_state.page="dashboard"
    # if st.sidebar.button("➕ Single QR"): st.session_state.page="single"
    # if st.sidebar.button("📂 Bulk QR"): st.session_state.page="bulk"
    # if st.sidebar.button("👤 Profile"): st.session_state.page="profile"

    st.sidebar.markdown("---")

    if st.sidebar.button("🚪 Logout"):
        # st.markdown(f"<meta http-equiv='refresh' content='0; url={FASTAPI_BASE_URL}/logout'>", unsafe_allow_html=True)
        # st.markdown(f"<meta http-equiv='refresh' content='0; url=/logout'>", unsafe_allow_html=True)
        # st.markdown(f"[Click here to Login]({FASTAPI_BASE_URL}/login)")

        st.markdown(
        f"<meta http-equiv='refresh' content='0; url={FASTAPI_BASE_URL}/logout'>",
        unsafe_allow_html=True
        )
        
        st.stop()

    if st.session_state.page=="dashboard": dashboard_page(user_id,user_name,business,plan)
    elif st.session_state.page=="single": single_qr_page(user_id)
    elif st.session_state.page=="bulk": bulk_qr_page(user_id)
    elif st.session_state.page=="profile": profile_page(user_id)
