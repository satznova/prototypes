from streamlit import st
from datetime import date

# ============================================================
# CONCEPT 1: st.set_page_config
# This must be the FIRST Streamlit call in your script.
# It controls the browser tab title, icon, and layout width.
# layout="wide" gives you more horizontal space.
# ============================================================
st.set_page_config(
    page_title="Page Title",
    page_icon="📋",
    layout="centered",
    #layout = "wide",
)

