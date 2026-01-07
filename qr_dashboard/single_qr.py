
# import streamlit as st
# import qrcode, re
# from io import BytesIO
# from reportlab.lib.pagesizes import A4
# from reportlab.pdfgen import canvas
# from reportlab.lib.utils import ImageReader
# from ui.ui_layout import render_layout
# import requests

# from dotenv import load_dotenv
# import os

# load_dotenv(dotenv_path="../.env")
# FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL")


# QR_SIZES = {
#     "🎫 ID Card / Badge – 25mm (300px)": 300,
#     "🏷 Asset / Sticker – 35mm (420px)": 420,
#     "🪧 Poster / Notice Board – 75mm (885px)": 885,
#     "🏗 Banner / Hoarding – 150mm (1770px)": 1770
# }

# QR_TYPES = [
#     "🌐 Website Link",
#     "🆔 Code / Text (Employee ID, Student ID)",
#     "💬 WhatsApp Chat Link"
# ]

# def single_qr_page(user_id):

#     # render_layout(user_id)

#     st.markdown("## ➕ Single QR Code Generator")

#     if "qr_result" not in st.session_state:
#         st.session_state.qr_result = None

#     with st.container(border=True):
#         col1, col2 = st.columns(2)

#         with col1:
#             qr_type = st.selectbox("What do you want to encode?", QR_TYPES)

#         with col2:
#             size_label = st.selectbox("Where will you print this QR?", list(QR_SIZES.keys()))

#         if qr_type == "🌐 Website Link":
#             data = st.text_input("Enter Website URL")
#         elif qr_type == "🆔 Code / Text (Employee ID, Student ID)":
#             data = st.text_input("Enter Code / Text (Max 50 chars)")
#         else:
#             data = st.text_input("Enter WhatsApp Number", placeholder="919876543210")

#         b1, b2, b3, b4, b5 = st.columns([3,1.5,0.2,1.5,3])
#         with b2:
#             gen = st.button("⚙ Generate QR")
#         with b4:
#             clr = st.button("🔄 Reset")

#     if clr:
#         st.session_state.qr_result = None
#         st.rerun()

#     if gen and data:
#         valid = True
#         file_name = "qr.png"

#         if qr_type == "🌐 Website Link":
#             if not data.startswith(("http://", "https://")):
#                 st.error("Website must start with http:// or https://")
#                 valid = False
#             file_name = "qr_website.png"

#         elif qr_type == "💬 WhatsApp Chat Link":
#             if not re.match(r"^\d{10,15}$", data):
#                 st.error("WhatsApp number must contain only digits (10–15)")
#                 valid = False
#             data = f"https://wa.me/{data}"
#             file_name = "qr_whatsapp.png"

#         else:
#             if len(data) > 50:
#                 st.error("Code/Text must be less than 50 characters")
#                 valid = False
#             file_name = f"qr_id_{data}.png".replace(" ", "_")

#         if valid:
#             qr = qrcode.QRCode(box_size=10, border=4)
#             qr.add_data(data)
#             qr.make(fit=True)

#             img = qr.make_image(fill_color="black", back_color="white")
#             size = QR_SIZES[size_label]
#             img = img.resize((size, size))

#             img_buf = BytesIO()
#             img.save(img_buf, format="PNG")

#             pdf_buf = BytesIO()
#             c = canvas.Canvas(pdf_buf, pagesize=A4)
#             w, h = A4
#             c.drawImage(ImageReader(img_buf), w/2-100, h/2-100, 200, 200)
#             c.save()

#             st.session_state.qr_result = {
#                 "img": img_buf.getvalue(),
#                 "pdf": pdf_buf.getvalue(),
#                 "file": file_name
#             }

#     if st.session_state.qr_result:
#         st.success("QR Generated Successfully")
#         st.image(st.session_state.qr_result["img"])

#         col1, col2 = st.columns(2)
#         with col1:
#             st.download_button("⬇ Download PNG",
#                 st.session_state.qr_result["img"],
#                 st.session_state.qr_result["file"])

#         with col2:
#             st.download_button("🖨 Print QR (PDF)",
#                 st.session_state.qr_result["pdf"],
#                 "AIROBOHUB_QR_PRINT.pdf")


#     requests.post(
#         f"{FASTAPI_BASE_URL}/api/log-usage/{user_id}",
#         data={"event_type": "single", "count": 1}
#     )

import streamlit as st
import qrcode, re, os, requests
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL")

QR_SIZES = {
    "🎫 ID Card / Badge – 25mm (300px)": 300,
    "🏷 Asset / Sticker – 35mm (420px)": 420,
    "🪧 Poster / Notice Board – 75mm (885px)": 885,
    "🏗 Banner / Hoarding – 150mm (1770px)": 1770
}

QR_TYPES = [
    "🌐 Website Link",
    "🆔 Code / Text (Employee ID, Student ID)",
    "💬 WhatsApp Chat Link"
]

def single_qr_page(user_id):

    if "single_logged" not in st.session_state:
        st.session_state.single_logged = False

    st.markdown("## ➕ Single QR Generator")

    qr_type = st.selectbox("What do you want to encode?", QR_TYPES)
    size_label = st.selectbox("Print Size", list(QR_SIZES.keys()))

    data = st.text_input("Enter Value")

    b1,b2,b3,b4,b5 = st.columns([3,1.5,0.2,1.5,3])
    with b2: gen = st.button("⚙ Generate QR")
    with b4: clr = st.button("🔄 Reset")

    if clr:
        st.session_state.qr_result = None
        st.session_state.single_logged = False
        st.rerun()

    if gen and data:
        valid = True
        if qr_type == "🌐 Website Link" and not data.startswith(("http://","https://")):
            st.error("Website must start with http:// or https://")
            valid = False

        if qr_type == "💬 WhatsApp Chat Link":
            if not re.match(r"^\d{10,15}$", data):
                st.error("WhatsApp number must contain only digits (10–15)")
                valid = False
            data = f"https://wa.me/{data}"

        if valid:
            qr = qrcode.make(data)
            qr = qr.resize((QR_SIZES[size_label],QR_SIZES[size_label]))

            img_buf = BytesIO()
            qr.save(img_buf,format="PNG")

            pdf_buf = BytesIO()
            c = canvas.Canvas(pdf_buf,pagesize=A4)
            w,h = A4
            c.drawImage(ImageReader(img_buf),w/2-100,h/2-100,200,200)
            c.save()

            st.session_state.qr_result = {
                "img":img_buf.getvalue(),
                "pdf":pdf_buf.getvalue()
            }

            if not st.session_state.single_logged:
                requests.post(f"{FASTAPI_BASE_URL}/api/log-usage/{user_id}",
                              data={"event_type":"single","count":1})
                st.session_state.single_logged = True

    if st.session_state.get("qr_result"):
        st.image(st.session_state.qr_result["img"])
        st.download_button("⬇ Download PNG",st.session_state.qr_result["img"],"qr.png")
        st.download_button("🖨 Print QR (PDF)",st.session_state.qr_result["pdf"],"qr_print.pdf")

