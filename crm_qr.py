import streamlit as st
from qr_dashboard.ui.ui_footer import ui_footer
from qr_dashboard.ui.ui_header import render
from qr_dashboard.ui.ui_footer import render as footer

def app():
    render("CRM Integration", "QR based lead capture into CRM")
    st.info("CRM Integration Coming Soon...")
    footer()
