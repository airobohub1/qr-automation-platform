import streamlit as st
import qrcode
from io import BytesIO
from ui_header import render
from ui_footer import render as footer

def app():
    render("Single QR Generator", "Generate QR instantly for any URL")

    url = st.text_input("Enter Website URL")
    if st.button("Generate QR Code") and url:
        qr = qrcode.make(url)
        buf = BytesIO()
        qr.save(buf, format="PNG")
        st.image(buf.getvalue(), width=200)
        st.download_button("Download QR", buf.getvalue(), "qr.png")

    footer()
