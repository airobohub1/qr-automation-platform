import streamlit as st
from ..services import get_usage

def dashboard_page(user_id, user_name, business, plan):
    try:
        usage = get_usage(user_id).json()
    except:
        usage={"today":0,"total":0,"remaining":0}

    st.title("📊 QR Automation Dashboard")
    # st.markdown(f"### Welcome, **{user_name}**  \n🏢 {business}")
    st.markdown(f"""
        ### 👤 {user_name}
        🏢 **Business:** {business}  
        💼 **Plan:** {plan.upper()}
        """)

    c1,c2,c3=st.columns(3)
    c1.metric("Today",usage["today"])
    c2.metric("Total Used",usage["total"])
    c3.metric("Remaining",usage["remaining"])
