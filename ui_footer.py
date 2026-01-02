import streamlit as st

def render():
    st.markdown("""
    <style>
    .footer-box {
        margin-top:50px;
        padding:18px;
        border-top:1px solid #e0e0e0;
        text-align:center;
        font-size:13px;
        color:#6c757d;
        background:#fafafa;
    }
    .footer-strong {
        color:#333;
        font-weight:600;
    }
    </style>

    <div class="footer-box">
        <span class="footer-strong">
        Need Enterprise AI Solutions? We build GenAI Apps, Agentic AI Systems, Data Analytics Platforms & Automation Solutions.
        </span><br><br>
        🌐 Website: <a href="https://airobohub.com" target="_blank">https://airobohub.com</a> &nbsp;|&nbsp;
        📞 +91 7893688993 &nbsp;|&nbsp;
        👤 Ch Srinivasa Rao<br>
        ✉️ chrao@airobohub.com | airobohub@gmail.com
    </div>
    """, unsafe_allow_html=True)
