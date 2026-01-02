import streamlit as st
import pandas as pd
import qrcode
import zipfile
import os
from ui_header import render
from ui_footer import render as footer

def app():
    render("Bulk QR Generator", "Upload Excel file and download QR codes in ZIP format")

    with st.container(border=True):
        uploaded_file = st.file_uploader("Upload Excel file (.xlsx)", type=["xlsx"])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)

        if "url" not in df.columns:
            st.error("Excel must contain column named 'url'")
            return

        with st.container(border=True):
            if st.button("Generate Bulk QR Codes"):
                os.makedirs("qr_bulk", exist_ok=True)
                zip_path = "qr_bulk/qr_codes.zip"

                with zipfile.ZipFile(zip_path, "w") as zipf:
                    for i, row in df.iterrows():
                        url = row["url"]
                        qr = qrcode.make(url)
                        file_name = f"qr_{i+1}.png"
                        file_path = f"qr_bulk/{file_name}"
                        qr.save(file_path)
                        zipf.write(file_path, arcname=file_name)

                with open(zip_path, "rb") as f:
                    st.download_button("Download All QR Codes", f, "bulk_qr_codes.zip")

    footer()
