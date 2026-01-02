import streamlit as st
import qrcode
from io import BytesIO

st.set_page_config(page_title="AI ROBO HUB | QR Code Generator", layout="centered")

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
.title {
    font-size:32px;
    font-weight:700;
    text-align:center;
}
.subtitle {
    font-size:16px;
    text-align:center;
    color:#6c757d;
    margin-bottom:20px;
}
.box {
    border:1px solid #d0d0d0;
    border-radius:10px;
    padding:20px;
    margin-bottom:20px;
    background-color:#fafafa;
}
</style>
""", unsafe_allow_html=True)

# ---------- TITLE ----------
st.markdown('<div class="title">AI ROBO HUB – QR Code Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Generate QR Codes instantly for any website URL</div>', unsafe_allow_html=True)

# ---------- INPUT PANEL ----------
st.markdown('<div class="box">', unsafe_allow_html=True)
st.subheader("🔗 Enter Website URL")

url = st.text_input("Paste your URL below", placeholder="https://www.yourwebsite.com")

generate_btn = st.button("Generate QR Code")
st.markdown('</div>', unsafe_allow_html=True)

# ---------- OUTPUT PANEL ----------
st.markdown('<div class="box">', unsafe_allow_html=True)
st.subheader("📥 Generated QR Code")

if generate_btn:
    if url:
        qr = qrcode.make(url)
        buf = BytesIO()
        qr.save(buf, format="PNG")

        st.image(buf.getvalue(), width=250)
        st.download_button(
            label="Download QR Code",
            data=buf.getvalue(),
            file_name="AIROBOHUB_QR.png",
            mime="image/png"
        )
    else:
        st.warning("Please enter a valid URL")

st.markdown('</div>', unsafe_allow_html=True)
