import streamlit as st
import pandas as pd
import os
import datetime
import base64

# ==============================
# CONFIGURATION
# ==============================
st.set_page_config(page_title="Panchmahals Voter Info Viewer", layout="wide")

DATA_FILE = "data/voter_data.xlsx"
PDF_FOLDER = "pdfs"
LOG_FILE = "usage_log.txt"

# ==============================
# FUNCTION: LOG USER ACTION
# ==============================
def log_user_action(action):
    # os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_ip = st.session_state.get("user_ip", "unknown")
        f.write(f"[{timestamp}] {user_ip} - {action}\n")

# ==============================
# FUNCTION: LOAD DATA
# ==============================
@st.cache_data
def load_data():
    df = pd.read_excel(DATA_FILE)
    df = df.replace(to_replace=r"(Gothda|ગોઠડા)", value="Godhra", regex=True)
    return df

# ==============================
# FUNCTION: DISPLAY PDF INLINE
# ==============================
def display_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    pdf_display = f"""
    <iframe src="data:application/pdf;base64,{base64_pdf}" 
            width="100%" height="800px" type="application/pdf"></iframe>
    """
    st.markdown(pdf_display, unsafe_allow_html=True)

# ==============================
# HEADER + DISCLAIMER
# ==============================
st.title("📄 Panchmahals Voter Polling Station Finder")

st.markdown("""
> **Educational Purpose Only**  
> This tool is created **only for Panchmahals district** to demonstrate structured data extraction and visualization.  
> For customized versions for other districts, please contact 📧 **mahektech@gmail.com**
""")

st.divider()

# ==============================
# LOAD PREDEFINED EXCEL
# ==============================
if not os.path.exists(DATA_FILE):
    st.error("❌ Data file not found! Please ensure 'data/voter_data.xlsx' exists.")
    st.stop()

df = load_data()

# ==============================
# CASCADE FILTERS (SORTED)
# ==============================
st.subheader("🔍 Filter Voter Data")

col1, col2, col3 = st.columns(3)

with col1:
    taluko_list = sorted(df["Taluko"].dropna().unique().tolist())
    taluko = st.selectbox("Select Taluko", taluko_list)

with col2:
    rev_circle_list = sorted(
        df[df["Taluko"] == taluko]["Revenue Circle"].dropna().unique().tolist()
    )
    rev_circle = st.selectbox("Select Revenue Circle", rev_circle_list)

with col3:
    mukhya_gam_list = sorted(
        df[
            (df["Taluko"] == taluko) &
            (df["Revenue Circle"] == rev_circle)
        ]["Mukhya Gam nu Naam"].dropna().unique().tolist()
    )
    mukhya_gam = st.selectbox("Select Mukhya Gam", mukhya_gam_list)

filtered_df = df[
    (df["Taluko"] == taluko) &
    (df["Revenue Circle"] == rev_circle) &
    (df["Mukhya Gam nu Naam"] == mukhya_gam)
]

st.divider()

# ==============================
# ADDRESS SELECTION (SORTED)
# ==============================
st.subheader("🏫 Polling Station Details")

address_list = sorted(filtered_df["Matdar Kendra Sthan"].dropna().unique().tolist())
address = st.selectbox("Select Polling Station Address", address_list)

record = filtered_df[filtered_df["Matdar Kendra Sthan"] == address].iloc[0]
pdf_filename = record["Filename"]
pdf_path = os.path.join(PDF_FOLDER, pdf_filename)

# ==============================
# DISPLAY PDF INLINE
# ==============================
if os.path.exists(pdf_path):
    st.success("✅ PDF Found")
    st.write(f"**Polling Station Address:** {address}")
    st.download_button("📥 Download PDF", open(pdf_path, "rb"), file_name=pdf_filename)

    # Inline PDF viewer
    st.subheader("📘 Polling Station Document Preview")
    display_pdf(pdf_path)

    log_user_action(f"Viewed PDF: {pdf_filename}")
else:
    st.warning(f"⚠️ PDF not found: {pdf_filename}")

# ==============================
# SIDEBAR USAGE LOG
# ==============================
st.sidebar.header("📊 App Usage")

if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    st.sidebar.metric(label="Total User Actions", value=len(lines))
    st.sidebar.download_button("📜 Download Usage Log", "".join(lines), "usage_log.txt")
else:
    st.sidebar.write("No users logged yet.")

# ==============================
# FOOTER
# ==============================
st.divider()
st.markdown(
    "<p style='text-align: center; font-size:14px;'>Made for educational use — Panchmahals only. "
    "For other districts, contact <b>mahektech@gmail.com</b> 💡</p>",
    unsafe_allow_html=True
)
