import streamlit as st

def render(title, desc):
    st.markdown(f"""
    <div style="
        text-align:center;
        font-size:28px;
        font-weight:700;
        margin-bottom:5px;
        white-space:nowrap;
        ">
        AI ROBO HUB – {title}
    </div>
    <div style="text-align:center; font-size:14px; color:#666;">
        {desc}
    </div>
    <hr>
    """, unsafe_allow_html=True)
