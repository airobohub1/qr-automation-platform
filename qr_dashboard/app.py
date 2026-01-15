import streamlit as st
import os, requests
from dotenv import load_dotenv

from single_qr import single_qr_page
from bulk_qr import bulk_qr_page
from ui.ui_layout import render_layout


load_dotenv("../.env")
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL")

# ---------------- SAFE SESSION INIT ----------------
if "qr_session" not in st.session_state:
    st.session_state.qr_session = None

if "user" not in st.session_state:
    st.session_state.user = None
# --------------------------------------------------

params = st.query_params
token = params.get("token")

if token:
    st.session_state.qr_session = token
    st.query_params.clear()


resp = requests.get(
    f"{FASTAPI_BASE_URL}/api/validate-session",
    cookies=st.context.cookies
)

if resp.status_code != 200:
    st.markdown("## 🔐 Please Login to Continue")
    st.markdown(f"[Click here to Login]({FASTAPI_BASE_URL}/login)")
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

st.sidebar.markdown("""
<style>
div.stButton > button {
    width: 100% !important;
    height: 42px !important;
    margin-bottom: 6px;
}
</style>
""", unsafe_allow_html=True)




# import streamlit.components.v1 as components


# ---------- SECURE SESSION GUARD ----------

resp = requests.get(
    f"{FASTAPI_BASE_URL}/api/validate-session",
    cookies=st.context.cookies,
    timeout=5
)

if resp.status_code != 200:
    st.markdown("## 🔐 Please Login to Continue")
    st.markdown("[Click here to Login](http://127.0.0.1:8000/login)")
    st.stop()

user = resp.json()
user_id = user["id"]
user_name = user["name"]
business = user.get("business_name","")
plan = user.get("plan","free")


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
        f"<meta http-equiv='refresh' content='0; url={FASTAPI_BASE_URL}/logout'>",
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
    res = requests.get(f"{FASTAPI_BASE_URL}/api/profile/{user_id}")
    if res.status_code != 200:
        st.error("Unable to load profile")
        return

    profile = res.json()

    st.markdown("## 👤 My Profile")

    with st.form(f"profile_form_{user_id}"):
        name = st.text_input("Full Name", profile.get("name",""))
        business_name = st.text_input("Business Name", profile.get("business_name",""))
        business_info = st.text_area("Business Info", profile.get("business_info",""))
        mobile = st.text_input("Mobile", profile.get("mobile",""))
        location = st.text_input("Location", profile.get("location",""))
        email = st.text_input("Email", profile.get("email",""), disabled=True)

        save = st.form_submit_button("💾 Update Profile")

    if save:
        r = requests.post(
            f"{FASTAPI_BASE_URL}/api/profile/{user_id}",
            data={
                "name": name,
                "business_name": business_name,
                "mobile": mobile,
                "location": location,
                "business_info": business_info
            }
        )

        if r.status_code == 200:
            st.success("Profile updated successfully")
            st.rerun()
        else:
            st.error("Profile update failed")


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