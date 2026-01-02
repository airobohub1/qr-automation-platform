import streamlit as st

def apply_layout():
    st.markdown("""
    <style>
    section.main > div.block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
