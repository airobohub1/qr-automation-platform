import streamlit as st
from ui_header import render
from ui_footer import render as footer


def app():
    render("Bulk QR Generator", "Upload Excel file and generate QR codes in bulk")
    st.info("This feature will allow Excel upload and ZIP download of QR codes.")
    footer()