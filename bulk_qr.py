import streamlit as st
import pandas as pd
import qrcode
import zipfile
import os, base64
from ui_header import render
from ui_footer import render as footer

TEMPLATE_FILE = "qr_template.xlsx"

def create_template():
    df = pd.DataFrame({
        "company_name": ["Google", "OpenAI"],
        "url": ["https://google.com", "https://openai.com"],
        "status": ["Pending", "Pending"]
    })
    df.to_excel(TEMPLATE_FILE, index=False)

def right_download_link(file_path, label):
    with open(file_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    st.markdown(f"""
    <div style="width:100%; text-align:right; margin-bottom:5px;">
        <a href="data:application/octet-stream;base64,{b64}" download="{file_path}"
           style="font-size:13px; text-decoration:none; padding:4px 10px;
                  border:1px solid #ccc; border-radius:6px; color:#333;">
           ⬇ {label}
        </a>
    </div>
    """, unsafe_allow_html=True)

def app():
    render("Bulk QR Generator", "Upload Excel file and generate QR codes in bulk")

    if not os.path.exists(TEMPLATE_FILE):
        create_template()

    # Right aligned template link
    right_download_link(TEMPLATE_FILE, "Download Sample Excel")

    uploaded_file = st.file_uploader("Upload Filled Excel File", type=["xlsx"])

    if "generated" not in st.session_state:
        st.session_state.generated = False

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.dataframe(df, use_container_width=True)

        if st.button("⚙ Generate QR Codes"):
            os.makedirs("qr_bulk", exist_ok=True)
            zip_path = "qr_bulk/bulk_qr_codes.zip"

            with zipfile.ZipFile(zip_path, "w") as zipf:
                for i, row in df.iterrows():
                    name = str(row["company_name"]).replace(" ", "_").lower()
                    qr = qrcode.make(row["url"])
                    file_name = f"{name}.png"
                    file_path = f"qr_bulk/{file_name}"
                    qr.save(file_path)
                    zipf.write(file_path, arcname=file_name)
                    df.at[i, "status"] = "Completed"

            excel_path = "qr_bulk/updated_status.xlsx"
            df.to_excel(excel_path, index=False)

            st.session_state.generated = True
            st.session_state.zip_path = zip_path
            st.session_state.excel_path = excel_path

    if st.session_state.generated:
        col1, col2 = st.columns(2)

        with col1:
            with open(st.session_state.zip_path, "rb") as f:
                st.download_button("⬇ Download QR Codes ZIP", f, "bulk_qr_codes.zip")

        with col2:
            with open(st.session_state.excel_path, "rb") as f:
                st.download_button("⬇ Download Updated Excel", f, "updated_status.xlsx")

    footer()
