import streamlit as st

from src import frontend_main

st.set_page_config(layout="wide")

st.title("【料理作成】")

col1, col2 = st.columns(2)

with col1:
    frontend_main.start_cooking()

with col2:

    frontend_main.show_cookings_registered()

    st.header("PFCバランスはこちら")
    with st.expander("料理のPFCバランス"):
        frontend_main.show_nutrition_info_of_cooking()

    st.header("冷蔵庫の食材はこちら")
    with st.expander("冷蔵庫の食材"):
        frontend_main.show_refrigerator_fooddata()
