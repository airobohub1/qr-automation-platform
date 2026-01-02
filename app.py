import streamlit as st
import single_qr
import bulk_qr
import crm_qr

st.set_page_config(
    page_title="AI ROBO HUB – QR Automation Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------- SIDEBAR BRANDING ----------
st.sidebar.markdown("""
<div style='text-align:center; font-size:20px; font-weight:700;'>
AI ROBO HUB
</div>
<div style='text-align:center; font-size:12px; color:gray; margin-bottom:15px;'>
QR Automation Platform
</div>
<hr>
""", unsafe_allow_html=True)

menu = st.sidebar.radio(
    "Select Use Case",
    ["Single QR Generator", "Bulk QR Generator", "CRM Integration"]
)

# -------- PAGE ROUTING ----------
if menu == "Single QR Generator":
    single_qr.app()

elif menu == "Bulk QR Generator":
    bulk_qr.app()

elif menu == "CRM Integration":
    crm_qr.app()
