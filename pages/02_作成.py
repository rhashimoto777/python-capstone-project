import streamlit as st

from src import frontend_main

st.set_page_config(layout="wide")

st.title("料理を作りましょう")

col1, col2 = st.columns(2)

with col1:
    frontend_main.start_cooking()

with col2:

    frontend_main.show_cookings_registered()
    frontend_main.show_refrigerator_fooddata()
