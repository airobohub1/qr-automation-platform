import streamlit as st

def render_layout(user_id):
    st.markdown(
        f"""
        <div style="background:#4f46e5;padding:15px;border-radius:8px;margin-bottom:15px">
            <h3 style="color:white;">AI ROBO HUB – QR Automation Platform</h3>
            <p style="color:white;">Logged in User ID: {user_id}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
