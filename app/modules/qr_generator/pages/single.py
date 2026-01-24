
import streamlit as st
import qrcode, re, os, requests
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from dotenv import load_dotenv

load_dotenv("../.env")
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL")

QR_SIZES = {
    "Please Select Print Size": None,
    "🎫 ID Card / Badge – 25mm (300px)": 300,
    "🏷 Asset / Sticker – 35mm (420px)": 420,
    "🪧 Poster / Notice Board – 75mm (885px)": 885,
    "🏗 Banner / Hoarding – 150mm (1770px)": 1770
}

QR_TYPES = [
    "Please Select Type",
    "🌐 Website Link",
    "🆔 Code / Text (Employee ID, Student ID)",
    "💬 WhatsApp Chat Link"
]

def single_qr_page(user_id):

    st.markdown("## ➕ Single QR Generator")

    if "qr_result" not in st.session_state:
        st.session_state.qr_result = None
    if "qr_logged" not in st.session_state:
        st.session_state.qr_logged = False

    qr_type = st.selectbox("What do you want to encode?", QR_TYPES, index=0)
    size_label = st.selectbox("Where will you print this QR?", list(QR_SIZES.keys()), index=0)
    data = st.text_input("Enter Value")

    b1,b2,b3,b4,b5 = st.columns([3,1.5,0.2,1.5,3])
    with b2: gen = st.button("⚙ Generate QR")
    with b4: reset = st.button("🔄 Reset")

    if reset:
        for k in ["qr_result","qr_logged"]:
            st.session_state.pop(k,None)
        st.rerun()

    # ---------- QUOTA CHECK ----------
    if gen:
        if qr_type=="Please Select Type" or size_label=="Please Select Print Size":
            st.error("Please select QR Type and Print Size.")
            return

        try:
            q = requests.get(f"{FASTAPI_BASE_URL}/api/check-quota/{user_id}",timeout=10)
            quota = q.json()
        except:
            st.error("❌ Unable to check quota")
            return
        
        if "daily_remaining" not in quota:
            st.error(quota.get("detail", "Quota information not available"))
            st.stop()

        if quota["daily_remaining"]<=0 or quota["total_remaining"]<=0:
            st.error("❌ QR Limit Reached. Upgrade your plan.")
            return

    # ---------- GENERATE QR ----------
    if gen and data:

        valid=True

        if qr_type=="🌐 Website Link" and not data.startswith(("http://","https://")):
            st.error("Website must start with http:// or https://")
            valid=False

        if qr_type=="💬 WhatsApp Chat Link":
            if not re.match(r"^\d{10,15}$",data):
                st.error("WhatsApp number must contain only digits (10–15)")
                valid=False
            data=f"https://wa.me/{data}"

        if valid:

            qr=qrcode.make(data)
            qr=qr.resize((QR_SIZES[size_label],QR_SIZES[size_label]))

            img_buf=BytesIO()
            qr.save(img_buf,format="PNG")

            pdf_buf=BytesIO()
            c=canvas.Canvas(pdf_buf,pagesize=A4)
            w,h=A4
            c.drawImage(ImageReader(img_buf),w/2-100,h/2-100,200,200)
            c.save()

            st.session_state.qr_result={
                "img":img_buf.getvalue(),
                "pdf":pdf_buf.getvalue()
            }

            # -------- LOG USAGE ONCE --------
            if not st.session_state.qr_logged:
                requests.post(f"{FASTAPI_BASE_URL}/api/log-usage/{user_id}",
                              data={"event_type":"single","count":1})
                st.session_state.qr_logged=True

    # ---------- OUTPUT ----------
    if st.session_state.qr_result:
        st.success("QR Generated Successfully")
        st.image(st.session_state.qr_result["img"])
        st.download_button("⬇ Download PNG",st.session_state.qr_result["img"],"qr.png")
        st.download_button("🖨 Print QR (PDF)",st.session_state.qr_result["pdf"],"qr_print.pdf")
