import streamlit as st

def render(title, desc):
    st.markdown(f"""
    <style>
    .brand-header {{
        text-align:center;
        font-size:30px;
        font-weight:800;
        background: linear-gradient(90deg,#0052D4,#4364F7,#6FB1FC);
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
        margin-bottom:2px;
        white-space:nowrap;
    }}
    .brand-desc {{
        text-align:center;
        font-size:15px;
        color:#6c757d;
        margin-bottom:10px;
    }}
    .divider {{
        height:2px;
        background:#e0e0e0;
        margin-bottom:20px;
    }}
    </style>

    <div class="brand-header">AI ROBO HUB – {title}</div>
    <div class="brand-desc">{desc}</div>
    <div class="divider"></div>
    """, unsafe_allow_html=True)
