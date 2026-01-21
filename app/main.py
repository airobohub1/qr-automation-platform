import streamlit as st
# from app.modules.qr_generator.router import qr_router

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.modules.qr_generator.router import qr_router


if __name__ == "__main__":
    qr_router()
