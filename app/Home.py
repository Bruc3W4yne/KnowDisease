import streamlit as st
from utils.backend_init import get_pipeline, get_graph_builder

st.set_page_config(
    page_title="LLMDap Dashboard",
    page_icon="chart",
    layout="wide",
    initial_sidebar_state="collapsed"
)

get_pipeline()
get_graph_builder()

st.title("LLMDap Dashboard")
st.markdown("Welcome to LLMDap. View your metrics and recent extraction runs.")
st.divider()

st.subheader("Pipeline Health")
col1, col2, col3 = st.columns(3)
with col1:
    with st.container(border=True):
        st.metric(label="F-Score", value="0.87", delta="2.3%")
with col2:
    with st.container(border=True):
        st.metric(label="Precision", value="0.92", delta="-1.2%", delta_color="normal")
with col3:
    with st.container(border=True):
        st.metric(label="Recall", value="0.83", delta="0.8%", delta_color="normal")

st.divider()

col_left_btn, col_mid_btn, col_right_btn = st.columns([3, 1, 1])

with col_right_btn:
    if st.button("Upload Article", type="primary"):
        try:
            st.switch_page("pages/1_Upload.py")
        except Exception as e:
            st.error(f"Navigation failed. Ensure page exists and Streamlit >= 1.27. Error: {e}")

st.divider()
st.subheader("Recent Runs")
st.markdown("_(Recent runs table will appear here when connected to metrics database)_")

st.divider()
st.caption("LLMDap v1.0 - SINTEF Project")