from src import frontend_main
from src import translator
import streamlit as st

st.set_page_config(
    page_title="My cooking", 
    page_icon=None, 
    layout="wide", 
    initial_sidebar_state="auto", 
)

st.title("冷蔵庫の食材から料理を登録しましょう")

st.markdown(
    """
    <style>
    /* マルチセレクトを含むすべての入力部分の幅を狭くする */
    div[data-baseweb="input"] > div, 
    div[data-baseweb="select"] > div,
    div[data-baseweb="textarea"] > div,
    div[data-baseweb="checkbox"] > div {
        width: 300px;
    }
    </style>
    """,unsafe_allow_html=True)


col1, col2= st.columns(2)
with col1:

    frontend_main.choice_food()
    frontend_main.resister_cooking()
    

with col2:
    st.header('冷蔵庫の食材はこちら')
    with st.expander("冷蔵庫の食材"):
        frontend_main.show_refrigerator_fooddata()

    frontend_main.show_cookings_registered()