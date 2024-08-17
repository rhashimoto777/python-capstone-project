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

tab1, tab2, tab3 = st.tabs(["料理一覧", "PFCバランス", "カロリー摂取"])

with tab1:
    st.subheader("料理一覧")
    frontend_main.show_cookinghistory_registered()

with tab2:
    st.subheader("PFCバランス")
    frontend_main.show_nutrition_info_of_cooking()

with tab3:
    st.subheader("カロリー摂取")
    with st.expander("None"):
        frontend_main.show_refrigerator_fooddata()
