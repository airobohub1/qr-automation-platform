# import streamlit as st
# import pandas as pd
# import qrcode, os, zipfile, re, requests
# from dotenv import load_dotenv

# load_dotenv(dotenv_path="../.env")
# FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL")

# QR_SIZES = {
#     "🎫 ID Card / Badge – 25mm (300px)": 300,
#     "🏷 Asset / Sticker – 35mm (420px)": 420,
#     "🪧 Poster / Notice Board – 75mm (885px)": 885,
#     "🏗 Banner / Hoarding – 150mm (1770px)": 1770
# }

# QR_TYPES = ["🌐 Website Link", "🆔 Code / Text", "💬 WhatsApp Number"]
# TEMPLATE_FILE = "bulk_qr_template.xlsx"


# def create_template():
#     pd.DataFrame({"value": ["https://airobohub.com"], "status": ["Pending"]}) \
#       .to_excel(TEMPLATE_FILE, index=False)


# def safe_filename(v):
#     return re.sub(r'[\\/*?:"<>|]', "_", str(v))[:40]


# def bulk_qr_page(user_id):

#     if "bulk_state" not in st.session_state:
#         st.session_state.bulk_state = {}

#     st.markdown("## 📂 Bulk QR Generator")

#     if not os.path.exists(TEMPLATE_FILE):
#         create_template()

#     with open(TEMPLATE_FILE, "rb") as f:
#         st.download_button("⬇ Download Sample Excel", f, TEMPLATE_FILE)

#     qr_type = st.selectbox("QR Type", QR_TYPES)
#     size_label = st.selectbox("Print Size", list(QR_SIZES.keys()))
#     uploaded_file = st.file_uploader("Upload Filled Excel File", type=["xlsx"])

#     if not uploaded_file and not st.session_state.bulk_state:
#         st.info("Upload Excel file to generate QR codes.")
#         return

#     gen_clicked = st.button("⚙ Generate Bulk QR Codes")

#     if gen_clicked and uploaded_file:
#         df = pd.read_excel(uploaded_file)

#         if not {"value","status"}.issubset(df.columns):
#             st.error("Excel must contain only columns: value, status")
#             return

#         out_dir = "bulk_qr_output"
#         os.makedirs(out_dir, exist_ok=True)
#         zip_path = f"{out_dir}/bulk_qr_codes.zip"
#         errors = []

#         with zipfile.ZipFile(zip_path,"w") as zipf:
#             for i,row in df.iterrows():
#                 raw = str(row["value"])
#                 data = raw
#                 valid = True

#                 if qr_type == "🌐 Website Link" and not raw.startswith(("http://","https://")):
#                     valid = False

#                 if qr_type == "💬 WhatsApp Number":
#                     if not re.match(r"^\d{10,15}$", raw):
#                         valid = False
#                     data = f"https://wa.me/{raw}"

#                 if valid:
#                     qr = qrcode.make(data)
#                     qr = qr.resize((QR_SIZES[size_label],QR_SIZES[size_label]))
#                     fname = safe_filename(raw)+".png"
#                     path = os.path.join(out_dir,fname)
#                     qr.save(path)
#                     zipf.write(path,arcname=fname)
#                     df.at[i,"status"]="Completed"
#                 else:
#                     df.at[i,"status"]="Failed"
#                     errors.append({"Row":i+1,"Value":raw})

#         excel_path = f"{out_dir}/bulk_qr_status.xlsx"
#         df.to_excel(excel_path,index=False)

#         total = len(df[df["status"]=="Completed"])
#         requests.post(f"{FASTAPI_BASE_URL}/api/log-usage/{user_id}",
#                       data={"event_type":"bulk","count":total})

#         st.session_state.bulk_state = {
#             "zip": zip_path,
#             "excel": excel_path,
#             "errors": errors
#         }

#     if st.session_state.bulk_state:
#         st.success("Bulk QR Codes generated successfully!")

#         with open(st.session_state.bulk_state["zip"],"rb") as f:
#             st.download_button("⬇ Download QR ZIP", f, "bulk_qr_codes.zip")

#         with open(st.session_state.bulk_state["excel"],"rb") as f:
#             st.download_button("⬇ Download Status Excel", f, "bulk_qr_status.xlsx")

#         if st.session_state.bulk_state["errors"]:
#             st.dataframe(pd.DataFrame(st.session_state.bulk_state["errors"]))

import streamlit as st
import pandas as pd
import qrcode, os, zipfile, re, requests
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL")

QR_SIZES = {
    "🎫 ID Card / Badge – 25mm (300px)": 300,
    "🏷 Asset / Sticker – 35mm (420px)": 420,
    "🪧 Poster / Notice Board – 75mm (885px)": 885,
    "🏗 Banner / Hoarding – 150mm (1770px)": 1770
}

QR_TYPES = ["🌐 Website Link","🆔 Code / Text","💬 WhatsApp Number"]
TEMPLATE_FILE="bulk_qr_template.xlsx"

def bulk_qr_page(user_id):

    if "bulk_logged" not in st.session_state:
        st.session_state.bulk_logged=False

    st.markdown("## 📂 Bulk QR Generator")

    if not os.path.exists(TEMPLATE_FILE):
        pd.DataFrame({"value":["https://airobohub.com"],"status":["Pending"]})\
          .to_excel(TEMPLATE_FILE,index=False)

    with open(TEMPLATE_FILE,"rb") as f:
        st.download_button("⬇ Download Sample Excel",f,TEMPLATE_FILE)

    qr_type = st.selectbox("QR Type",QR_TYPES)
    size_label = st.selectbox("Print Size",list(QR_SIZES.keys()))
    uploaded_file = st.file_uploader("Upload Excel",type=["xlsx"])

    gen = st.button("⚙ Generate Bulk QR Codes")

    if gen and uploaded_file:
        df=pd.read_excel(uploaded_file)
        out_dir="bulk_qr_output";os.makedirs(out_dir,exist_ok=True)
        zip_path=f"{out_dir}/bulk_qr_codes.zip"
        errors=[]

        with zipfile.ZipFile(zip_path,"w") as zipf:
            for i,row in df.iterrows():
                raw=str(row["value"])
                data=raw;valid=True
                if qr_type=="🌐 Website Link" and not raw.startswith(("http://","https://")): valid=False
                if qr_type=="💬 WhatsApp Number":
                    if not re.match(r"^\d{10,15}$",raw): valid=False
                    data=f"https://wa.me/{raw}"
                if valid:
                    qr=qrcode.make(data).resize((QR_SIZES[size_label],QR_SIZES[size_label]))
                    fname=re.sub(r'[\\/*?:"<>|]',"_",raw)[:40]+".png"
                    path=os.path.join(out_dir,fname);qr.save(path);zipf.write(path,fname)
                    df.at[i,"status"]="Completed"
                else:
                    df.at[i,"status"]="Failed";errors.append({"Row":i+1,"Value":raw})

        df.to_excel(f"{out_dir}/bulk_qr_status.xlsx",index=False)
        total=len(df[df["status"]=="Completed"])

        if not st.session_state.bulk_logged:
            requests.post(f"{FASTAPI_BASE_URL}/api/log-usage/{user_id}",
                          data={"event_type":"bulk","count":total})
            st.session_state.bulk_logged=True

        st.download_button("⬇ Download ZIP",open(zip_path,"rb"),"bulk_qr.zip")

   