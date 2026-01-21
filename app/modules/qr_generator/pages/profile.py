import streamlit as st
from ..services import get_profile, update_profile

def profile_page(user_id):
    res = get_profile(user_id)
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
        r = update_profile(user_id,{
            "name":name,
            "business_name":business_name,
            "mobile":mobile,
            "location":location,
            "business_info":business_info
        })
        if r.status_code==200:
            st.success("Profile updated successfully")
            st.rerun()
        else:
            st.error("Profile update failed")

