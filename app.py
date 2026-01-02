import streamlit as st
import single_qr
import bulk_qr
import crm_qr

st.set_page_config(page_title="AI ROBO HUB – QR Automation Platform", layout="wide")

st.sidebar.title("AI ROBO HUB")
menu = st.sidebar.radio("Select Use Case",
    ["Single QR Generator", "Bulk QR Generator", "CRM Integration"]
)

if menu == "Single QR Generator":
    single_qr.app()
elif menu == "Bulk QR Generator":
    bulk_qr.app()
else:
    crm_qr.app()
