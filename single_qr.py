import streamlit as st
import qrcode
from io import BytesIO
from ui_header import render
from ui_footer import render as footer

def app():
    render("Single QR Generator", "Generate QR codes instantly for any website URL")

    with st.container(border=True):
        url = st.text_input("Enter Website URL")
        generate_btn = st.button("Generate QR Code")

    with st.container(border=True):
        if generate_btn and url:
            qr = qrcode.make(url)
            buf = BytesIO()
            qr.save(buf, format="PNG")
            st.image(buf.getvalue(), width=250)
            st.download_button("Download QR Code", buf.getvalue(), "AIROBOHUB_QR.png")

    # ✅ Footer must be LAST line inside function
    footer()
