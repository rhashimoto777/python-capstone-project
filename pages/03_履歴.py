from src import frontend_main
from src import translator
import streamlit as st

st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
    /* 選択されたタブのスタイルを強制的に適用 */
    div[role="tablist"] > div[aria-selected="true"] {
        background-color: #FFFF00 !important; /* 背景色を黄色に設定 */
        color: #008000 !important; /* 文字色を緑に設定 */
        font-size: 20px !important; /* 文字サイズを20pxに設定 */
        font-weight: 700 !important; /* 文字を太字に設定 */
        border-radius: 0px !important; /* 丸みをなくす */
        border: 2px solid #004a55 !important; /* 外枠を色付きにする */
    }

    /* 選択されていないタブのスタイルも調整可能 */
    div[role="tablist"] > div {
        background-color: #FFFFFF !important; /* 背景色を白に設定 */
        color: #004a55 !important; /* 文字色を変更 */
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.title("作った料理を確認しましょう")

tab1, tab2, tab3 = st.tabs(["料理一覧", "PFCバランス", "カロリー摂取"])

with tab1:
   st.header("料理一覧")
   frontend_main.show_cookinghistory_registered()

with tab2:
   st.header("PFCバランス")
   frontend_main.show_nutrition_info_of_cooking()

with tab3:
   st.header("カロリー摂取")
   with st.expander("sw"):
      frontend_main.show_refrigerator_fooddata()