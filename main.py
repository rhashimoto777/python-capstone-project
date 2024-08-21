import streamlit as st

from src import translator

st.set_page_config(
    page_title="My cooking",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="auto",
)


# ________________________________________________________________________________________________________________________
def main_page():
    """
    Streamlitの仕様上、main.pyに対応するページが必ず出来てしまう。
    そのため、mainページに対応する表示処理をmain.py内から呼び出す必要がある。
    mainページを表示するための関数であるため、"main_page"という関数名にしておく。

    また、この関数が一番最初に実行されるため、各種初回処理を行う。
    """
    userman, login_id = translator.get_user_id_manager()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("ユーザーの切り替え")

        selected_user = st.selectbox("ユーザーを選択してください", userman.user_id_list)

    if selected_user is not None:
        bt = st.button(
            "＜ユーザーを切り替える＞",
            key="main_page_user_switch_conform",
        )
        if bt:
            translator.switch_user(selected_user)
            st.success(f"【{selected_user}】に切り替えました")
            st.balloons()

    with col2:
        st.subheader("＜ユーザーの新規追加＞")
        new_user_name = st.text_input("新しいユーザー名を登録してください")

        if new_user_name in userman.user_id_list:
            st.error("同じユーザーが既に存在します")
        else:
            bt = st.button(
                "ユーザーを作成",
                key="main_page_create_conform",
            )
            if bt:
                translator.switch_user(new_user_name)
                st.success(f"【{new_user_name}】を作成しました。")
                st.success(f"【{new_user_name}】に切り替えました。")
                st.balloons()

    userman, login_id = translator.get_user_id_manager()
    st.header(f"... 現在ログインしているユーザーは【{login_id}】です")
    return


if __name__ == "__main__":
    userman, login_id = translator.get_user_id_manager()
    print(
        "[system-message] ------------------------main function called------------------------"
    )
    del login_id
    translator.switch_user(userman.current_user)
    main_page()
