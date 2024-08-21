import os
import sys

from src import translator
from src.backend_app import common_info as common
from src.backend_app import user_id_manager

# プロジェクトのルートディレクトリを追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

PREFIX = "........."
ORIGINAL_CURRENT_USER = None


def pytest_configure(config):
    """
    全てのテストの計算よりも先に実行される関数
    """
    # 最後にログインしていたユーザーをバックアップ
    global ORIGINAL_CURRENT_USER
    userman = user_id_manager.UserIdManager()
    ORIGINAL_CURRENT_USER = userman.current_user

    # pytest用のDataBaseに切り替える
    user_id = "_PYTEST_"
    translator.switch_user(user_id)

    # pytest用のDataBaseを使うことを通知
    __line_separator()
    __msg_print(f"元々の最終利用ユーザーは、user_id = {ORIGINAL_CURRENT_USER} です。")
    __msg_print(f"pytest用のDataBaseを使用します。(user_id = {user_id})")

    # 前回のpytestの実行内容で影響を受けないよう、pytestを実行する度にDataBaseをバックアップから復元する。
    # まずはバックアップのDataBaseが存在するかを確認する。無ければraise Exceptionしてpytestは中止。
    __line_separator()
    check_backup_db_file_exist()

    # 次に既に「バックアップではない本体のDataBase」が存在するか確認し、あれば削除する。
    __line_separator()
    delete_existing_db_file()

    # これにて前処理は終了。pytestを実行することをユーザーに通知する。
    __line_separator()
    __msg_print("pytestの事前処理を完了。pytestを実行します。")
    __line_separator()
    return


def pytest_sessionfinish(session, exitstatus):
    """
    全てのテストが終了した後に実行されるteardown処理
    """
    print("\n")
    __line_separator()
    __msg_print("全てのテストを終了しました。teardown処理を実行します。")
    __line_separator()

    global ORIGINAL_CURRENT_USER
    translator.switch_user(ORIGINAL_CURRENT_USER)
    userman = user_id_manager.UserIdManager()
    __msg_print(f"user_id = {userman.current_user} に戻しました。")

    __line_separator()
    __msg_print("teardown処理を終了します")
    return


def __msg_print(msg):
    print(f"{PREFIX} {msg} {PREFIX}")


def __line_separator():
    print(".\n.")
    return


def check_backup_db_file_exist():
    db_bk_path = os.path.join(common.DB_DIR, common.DB_BACKUP_FILENAME)
    __msg_print(f"DataBaseのバックアップファイルが存在するか確認します。 {db_bk_path}")

    file_exist = os.path.exists(db_bk_path)
    if file_exist:
        __msg_print("OK。存在しました。")
    else:
        __msg_print("Error: ファイルが存在しません")
        raise Exception("Error")
    return


def delete_existing_db_file():
    db_path = os.path.join(common.DB_DIR, common.DB_FILENAME)
    __msg_print(f"既にDataBaseファイルが存在していれば消去します。 {db_path}")

    file_exist = os.path.exists(db_path)
    if file_exist:
        os.remove(db_path)
        __msg_print("消去しました。")
    else:
        __msg_print("ファイルが存在しませんでした。")
    return
