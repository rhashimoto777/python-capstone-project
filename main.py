from src import frontend_main, translator


# ________________________________________________________________________________________________________________________
def main_page():
    """
    Streamlitの仕様上、main.pyに対応するページが必ず出来てしまう。
    そのため、mainページに対応する表示処理をmain.py内から呼び出す必要がある。
    mainページを表示するための関数であるため、"main_page"という関数名にしておく。

    また、この関数が一番最初に実行されるため、各種初回処理を行う。
    """
    # TBD : ユーザーIDの選択UI

    # ************************************
    # translatorクラス内でBackEndOperatorのインスタンスを生成する。
    # この時点でuser_idを渡し、ユーザーIDごとのDBを呼び出す。（何も指定しなければuser_default）
    # ************************************
    translator.init()

    # ************************************
    # frontend内でtranslator-APIを使う処理は必ず translator.init() を実行した後で行うこと。
    # そうしないとBackEndOperatorのインスタンスがまだ出来ていないので、各種APIが動作しない。
    # ************************************
    frontend_main.main_page()


if __name__ == "__main__":
    print(
        "[system-message] ------------------------main function called------------------------"
    )
    main_page()
