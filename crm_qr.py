import streamlit as st
from ui_header import render
from ui_footer import render as footer

def app():
    render("CRM Integration", "QR based lead capture into CRM")
    st.info("CRM Integration Coming Soon...")
    footer()
