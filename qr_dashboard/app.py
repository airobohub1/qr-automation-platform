# import streamlit as st

# st.set_page_config(page_title="AI ROBO HUB – QR Automation Platform", layout="wide")

# params = st.query_params
# user_id = params.get("user_id")

# if not user_id:
#     st.error("❌ Unauthorized Access")
#     st.stop()

# st.title("AI ROBO HUB – QR Automation Platform")
# st.success(f"Welcome User ID: {user_id}")

# st.markdown("### QR Code Dashboard")

# col1, col2 = st.columns(2)

# with col1:
#     st.button("➕ Generate Single QR")

# with col2:
#     st.button("📂 Bulk QR Upload")

import streamlit as st

st.set_page_config(page_title="AI ROBO HUB – QR Automation Platform", layout="wide")

# params = st.query_params
# user_id = params.get("user_id")

# if not user_id:
#     st.error("❌ Unauthorized Access")
#     st.stop()


from single_qr import single_qr_page
from bulk_qr import bulk_qr_page


import os

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
    st.title("📊 QR Automation Dashboard")

    st.markdown("### Welcome to AI ROBO HUB – QR Automation Platform")
    st.success(f"Logged in User ID: {user_id}")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Today's QR Usage", "0 / 10")

    with col2:
        st.metric("Plan", "FREE")

    with col3:
        st.metric("Status", "Active")

    st.markdown("---")
    st.write("Use left menu to generate Single or Bulk QR Codes.")


# def single_qr_page():
#     st.title("➕ Generate Single QR Code")
#     text = st.text_input("Enter Text / URL")
#     if st.button("Generate QR"):
#         st.success("QR Generated Successfully (mock)")

# def bulk_qr_page():
#     st.title("📂 Bulk QR Generator")
#     file = st.file_uploader("Upload CSV file")
#     if file:
#         st.success("Bulk QR Generated (mock)")


if st.session_state.page == "dashboard":
    dashboard_page()
elif st.session_state.page == "single":
    single_qr_page(user_id)
elif st.session_state.page == "bulk":
    bulk_qr_page(user_id)



