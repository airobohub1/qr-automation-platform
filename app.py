import streamlit as st
import qr_dashboard.single_qr as single_qr
import qr_dashboard.bulk_qr as bulk_qr
# import crm_qr
import requests
from auth_server import config

# from auth.auth_ui import register_ui, verify_ui, login_ui, forgot_password_ui
# from auth.auth_ui import login_ui, forgot_password_ui


if "auth" not in st.session_state:
    try:
        # r = requests.get("http://localhost:8000/ping")
        r = requests.get(f"{config.FASTAPI_BASE_URL}/ping")
        if r.status_code != 200:
            st.error("Auth Server not running. Start FastAPI first.")
            st.stop()
    except:
        st.error("Auth Server not running. Start FastAPI first.")
        st.stop()
        

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


# from auth.db import create_tables
# from auth.auth_ui import register_ui, verify_ui
# create_tables()

st.set_page_config(page_title="AI ROBO HUB - QR Automation Platform", layout="wide")

st.sidebar.title("AI ROBO HUB")
# menu = st.sidebar.radio("Menu",
#     ["Login","Register","Verify Email","Single QR Generator", "Bulk QR Generator"]
menu = st.sidebar.radio("Menu",
    ["Single QR Generator", "Bulk QR Generator"]

)

if menu == "Single QR Generator":
    single_qr.app()
elif menu == "Bulk QR Generator":
    bulk_qr.app()
# elif menu == "Register":
#     register_ui()
# elif menu == "Verify Email":
#     verify_ui()
# elif menu == "Login":
#     login_ui()
#     forgot_password_ui() 
# else:
#     crm_qr.app()
