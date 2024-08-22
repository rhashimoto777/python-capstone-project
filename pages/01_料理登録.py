import streamlit as st

from src import frontend_main

st.set_page_config(
    page_title="My cooking",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="auto",
)

# st.title("冷蔵庫の食材から料理を登録しましょう")

# st.markdown(
#     """
#     <style>
#     /* マルチセレクトを含むすべての入力部分の幅を狭くする */
#     div[data-baseweb="input"] > div,
#     div[data-baseweb="select"] > div,
#     div[data-baseweb="textarea"] > div,
#     div[data-baseweb="checkbox"] > div {
#         width: 600px;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )
st.title("【料理登録】")

col1, col2 = st.columns(2)
with col1:

    frontend_main.resister_cooking()


with col2:
    # st.header("冷蔵庫の食材はこちら")
    # with st.expander("冷蔵庫の食材"):
    #     frontend_main.show_refrigerator_fooddata()

    # frontend_main.show_cookings_registered()
    with st.form(key="sample_page_demo_call_frontend"):
        submit_btn1 = st.form_submit_button("「冷蔵庫の中にある食材の種類・数」を表示")
        submit_btn2 = st.form_submit_button("「登録済みの料理」を表示")
    if submit_btn1:
        frontend_main.show_refrigerator_fooddata()
    if submit_btn2:
        frontend_main.show_cookings_registered()
    del submit_btn1, submit_btn2
