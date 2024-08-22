import streamlit as st

from src import frontend_main

st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
    div[data-baseweb="tab"] > div:first-child > div[role="tablist"] > div[role="tab"]:first-child {
        background-color: #ff6347; /* 最初のタブが選択されている場合の背景色 */
        color: white;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


st.title("【料理履歴】")

st.subheader("料理一覧")
frontend_main.show_cookinghistory_registered()