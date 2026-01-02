import streamlit as st
from ui_header import render
from ui_footer import render as footer


def app():
    render("CRM Integration", "Capture leads via QR and sync directly to CRM")
    st.info("This module will push QR-based leads into CRM system.")

    footer()