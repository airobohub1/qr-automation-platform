import streamlit as st
import os, requests
from dotenv import load_dotenv
from single_qr import single_qr_page
from bulk_qr import bulk_qr_page
from ui.ui_layout import render_layout

load_dotenv("../.env")
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL")


resp = requests.get(
    f"{FASTAPI_BASE_URL}/api/validate-session",
    cookies=st.context.cookies
)

if resp.status_code != 200:
    st.markdown("## 🔐 Please Login to Continue")
    st.markdown("[Click here to Login](http://127.0.0.1:8000/login)")
    st.stop()

user = resp.json()
user_id   = user["id"]
user_name = user["name"]
business  = user.get("business_name","")
plan      = user.get("plan","FREE")



st.set_page_config(page_title="AI ROBO HUB – QR Automation Platform", layout="wide")

# ---------- STYLES ----------
st.markdown("""
<style>
.block-container { padding-top: 1rem !important; }
div.stButton > button { width: 100%; }
</style>
""", unsafe_allow_html=True)

# # ---------- SESSION VALIDATION ----------

# def validate_session():
#     try:
#         r = requests.get(
#             f"{FASTAPI_BASE_URL}/api/validate-session",
#             cookies=st.context.cookies,
#             timeout=5
#         )
#         if r.status_code != 200:
#             return None
#         return r.json()
#     except:
#         return None

# user = validate_session()

# if not user:
#     st.markdown("## 🔐 Please Login to Continue")
#     st.markdown("[Click here to Login](http://127.0.0.1:8000/login)")
#     st.stop()

# user_id   = user["id"]
# user_name = user["name"]
# business  = user.get("business_name","")
# plan      = user.get("plan","FREE")


import streamlit.components.v1 as components

# components.html("""
# <script>
# document.cookie.split(';').forEach(c => {
#     if (c.trim().startsWith("qr_session=")) {
#         fetch("/_stcore/set_session", {
#             method: "POST",
#             headers: {"Content-Type":"application/json"},
#             body: JSON.stringify({qr_session: c.split("=")[1]})
#         });
#     }
# });
# </script>
# """, height=0)


# def get_qr_session_cookie():
#     headers = st.experimental_get_query_params()
#     # return st.session_state.get("qr_session")


# if "qr_session" not in st.session_state:
#     # st.session_state.qr_session = None

# if not st.session_state.qr_session:
#     st.markdown("## 🔐 Please Login to Continue")
#     st.markdown("[Click here to Login](http://127.0.0.1:8000/login)")
#     st.stop()


# ---------- SECURE SESSION GUARD ----------

# resp = requests.get(
#     f"{FASTAPI_BASE_URL}/api/validate-session",
#     cookies=st.context.cookies
# )

# if resp.status_code != 200:
#     st.markdown("## 🔐 Please Login to Continue")
#     st.markdown("[Click here to Login](http://127.0.0.1:8000/login)")
#     st.stop()

# user = resp.json()
# user_id = user["id"]
# user_name = user["name"]
# business = user.get("business_name","")
# plan = user.get("plan","FREE")


# resp = requests.get(
#     f"{FASTAPI_BASE_URL}/api/validate-session",
#     headers={"Authorization": st.session_state.qr_session}
# )

# if resp.status_code != 200:
#     st.markdown("## 🔐 Please Login to Continue")
#     st.markdown("[Click here to Login](http://127.0.0.1:8000/login)")
#     st.stop()

# user = resp.json()
# user_id = user["id"]
# user_name = user["name"]
# business = user.get("business_name","")
# plan = user.get("plan","FREE")



# ---------- SECURE SESSION GUARD ----------
try:
    resp = requests.get(
        f"{FASTAPI_BASE_URL}/api/validate-session",
        cookies=st.context.cookies,
        timeout=5
    )
except:
    st.error("❌ Unable to reach authentication server")
    st.stop()

if resp.status_code != 200:
    st.markdown("## 🔐 Please Login to Continue")
    st.markdown("[Click here to Login](http://127.0.0.1:8000/login)")
    st.stop()

user = resp.json()
user_id = user["id"]
user_name = user["name"]
business = user.get("business_name","")
plan = user.get("plan","FREE")



# ---------- GLOBAL STATE ----------
if "page" not in st.session_state:
    st.session_state.page="dashboard"

# ---------- HEADER ----------
render_layout({
    "name":user_name,
    "business_name":business,
    "plan":plan
})

# ---------- SIDEBAR ----------
st.sidebar.title("AI ROBO HUB")
st.sidebar.markdown("### QR Automation Platform")

if st.sidebar.button("🏠 Dashboard"): st.session_state.page="dashboard"
if st.sidebar.button("➕ Single QR"): st.session_state.page="single"
if st.sidebar.button("📂 Bulk QR"): st.session_state.page="bulk"
if st.sidebar.button("👤 Profile"): st.session_state.page="profile"

st.sidebar.markdown("---")

if st.sidebar.button("🚪 Logout"):
    st.markdown(
        "<meta http-equiv='refresh' content='0;url=http://127.0.0.1:8000/logout'>",
        unsafe_allow_html=True
    )
    st.stop()


# ---------- DASHBOARD ----------
def dashboard_page():
    try:
        usage = requests.get(f"{FASTAPI_BASE_URL}/api/usage/{user_id}").json()
    except:
        usage={"today":0,"total":0,"remaining":0}

    st.title("📊 QR Automation Dashboard")
    st.markdown(f"### Welcome, **{user_name}**  \n🏢 {business}")

    c1,c2,c3=st.columns(3)
    c1.metric("Today",usage["today"])
    c2.metric("Total Used",usage["total"])
    c3.metric("Remaining",usage["remaining"])

# ---------- PROFILE ----------
def profile_page():
    res=requests.get(f"{FASTAPI_BASE_URL}/api/profile/{user_id}")
    profile=res.json()

    with st.form("profile_form"):
        name=st.text_input("Full Name",profile.get("name",""))
        business_name=st.text_input("Business Name",profile.get("business_name",""))
        mobile=st.text_input("Mobile",profile.get("mobile",""))
        save=st.form_submit_button("💾 Save")

    if save:
        requests.post(f"{FASTAPI_BASE_URL}/api/profile/{user_id}",data={
            "name":name,"business_name":business_name,"mobile":mobile
        })
        st.success("Profile updated")
        st.rerun()


#---------------lead form----------------

def lead_form(plan):
    st.markdown(f"## 🚀 {plan.upper()} PLAN – Get Started")

    with st.form("lead_form"):
        name = st.text_input("Full Name")
        business = st.text_input("Business Name")
        email = st.text_input("Email")
        mobile = st.text_input("Mobile")
        submit = st.form_submit_button("📨 Submit")

    if submit:
        requests.post(f"{FASTAPI_BASE_URL}/api/lead", data={
            "name": name,
            "business_name": business,
            "email": email,
            "mobile": mobile,
            "plan": plan
        })
        st.success("✅ Thank you! Our executive will contact you shortly.")
        st.button("⬅ Back to Dashboard", on_click=lambda: st.session_state.update({"page":"dashboard"}))



# ---------- ROUTER ----------
if st.session_state.page=="dashboard": dashboard_page()
elif st.session_state.page=="single": single_qr_page(user_id)
elif st.session_state.page=="bulk": bulk_qr_page(user_id)
elif st.session_state.page=="profile": profile_page()
