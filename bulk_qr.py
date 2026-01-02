import streamlit as st
import pandas as pd
import qrcode
import os, zipfile, re
from ui_header import render
from ui_footer import render as footer

QR_SIZES = {
    "🎫 ID Card / Badge – 25mm (300px)": 300,
    "🏷 Asset / Sticker – 35mm (420px)": 420,
    "🪧 Poster / Notice Board – 75mm (885px)": 885,
    "🏗 Banner / Hoarding – 150mm (1770px)": 1770
}

QR_TYPES = [
    "🌐 Website Link",
    "🆔 Code / Text",
    "💬 WhatsApp Number"
]

TEMPLATE_FILE = "bulk_qr_template.xlsx"

def create_template():
    df = pd.DataFrame({
        "value": ["https://airobohub.com"],
        "status": ["Pending"]
    })
    df.to_excel(TEMPLATE_FILE, index=False)

def safe_filename(value):
    return re.sub(r'[\\/*?:"<>|]', "_", value)[:40]

def app():
    render("Bulk QR Generator", "Generate enterprise-grade QR codes in bulk")

    if "bulk_result" not in st.session_state:
        st.session_state.bulk_result = None
    if "bulk_success" not in st.session_state:
        st.session_state.bulk_success = False

    if not os.path.exists(TEMPLATE_FILE):
        create_template()

    # ---------- Sample Excel (Right aligned) ----------
    col_spacer, col_link = st.columns([5,1])
    with col_link:
        with open(TEMPLATE_FILE, "rb") as f:
            st.download_button("Download Sample Excel", f, TEMPLATE_FILE)

    # ---------- Input Panel ----------
    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1:
            qr_type = st.selectbox("What do you want to encode?", QR_TYPES)
        with c2:
            size_label = st.selectbox("Where will you print this QR?", list(QR_SIZES.keys()))

        st.markdown("#### 📄 Excel File Format")
        st.markdown("""
        | Column | Description |
        |-------|-------------|
        | value | URL / ID / WhatsApp Number |
        | status | Keep as `Pending` |
        """)

        uploaded_file = st.file_uploader("Upload Filled Excel File", type=["xlsx"])

    # ---------- File Processing ----------
    if uploaded_file:
        df = pd.read_excel(uploaded_file)

        if not {"value","status"}.issubset(df.columns):
            st.error("Excel must contain only columns: value, status")
            footer()
            return

        st.dataframe(df, use_container_width=True)

        if st.button("⚙ Generate Bulk QR Codes"):
            out_dir = "bulk_qr_output"
            os.makedirs(out_dir, exist_ok=True)
            zip_path = f"{out_dir}/bulk_qr_codes.zip"

            progress = st.progress(0)
            status_text = st.empty()
            total = len(df)

            with zipfile.ZipFile(zip_path, "w") as zipf:
                for i, row in df.iterrows():
                    raw = str(row["value"])
                    data = raw
                    valid = True

                    if qr_type == "🌐 Website Link" and not raw.startswith(("http://","https://")):
                        valid = False

                    if qr_type == "💬 WhatsApp Number":
                        if not re.match(r"^\d{10,15}$", raw):
                            valid = False
                        data = f"https://wa.me/{raw}"

                    if not valid:
                        df.at[i,"status"] = "Failed"
                    else:
                        qr = qrcode.make(data)
                        qr = qr.resize((QR_SIZES[size_label], QR_SIZES[size_label]))

                        fname = safe_filename(raw) + ".png"
                        path = os.path.join(out_dir, fname)
                        qr.save(path)
                        zipf.write(path, arcname=fname)
                        df.at[i,"status"] = "Completed"

                    status_text.info(f"Processing {i+1} / {total} QR Codes...")
                    progress.progress(int((i+1)/total*100))

            status_text.success("QR generation completed!")
            progress.empty()

            excel_path = f"{out_dir}/bulk_qr_status.xlsx"
            df.to_excel(excel_path, index=False)

            st.session_state.bulk_result = {"zip": zip_path, "excel": excel_path}
            st.session_state.bulk_success = True

    # ---------- Output ----------
    if st.session_state.bulk_success:
        st.success("Bulk QR Codes generated successfully. Download them below.")

    if st.session_state.bulk_result:
        o1, o2 = st.columns(2)
        with o1:
            with open(st.session_state.bulk_result["zip"],"rb") as f:
                st.download_button("⬇ Download QR Codes ZIP", f, "bulk_qr_codes.zip")
        with o2:
            with open(st.session_state.bulk_result["excel"],"rb") as f:
                st.download_button("⬇ Download Updated Excel", f, "bulk_qr_status.xlsx")

    footer()
