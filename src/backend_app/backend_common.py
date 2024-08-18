import os
from pathlib import Path

# バックエンド内で参照するpath・ファイル名
ROOT_PATH = None
DB_PATH = None
DB_FILENAME = None
DB_BACKUP_FILENAME = None
FOODDATA_JSON_PATH = None
FOODDATA_JSON_FILENAME = None

USER_ID = None
INIT_FINISH = False

# ________________________________________________________________________________________________________________________
# global関数


def init(user_id="user_default"):
    """
    初回起動時の処理。
    pytest用に様々な場所から呼ぶため、既に計算している場合はskipする。
    """
    global INIT_FINISH
    if not INIT_FINISH:
        _memorize_user_id(user_id)
        _gen_root_path()
        _gen_fooddata_json_path_and_name()
        _gen_db_path_and_name(user_id)
        INIT_FINISH = True
    else:
        pass
    return


def system_msg_print(msg):
    """
    Backend側で用いるシステムメッセージ表示用のprint関数
    """
    print(f"[backend : system-message] {msg}")
    return


# ________________________________________________________________________________________________________________________
# private関数


def _gen_root_path():
    """
    最上位フォルダ (main.pyがあるフォルダ) のpathを取得し、グローバル変数に書き込む。
    """
    global ROOT_PATH
    current_path = Path(__file__).resolve().parent
    ROOT_PATH = current_path.parent.parent
    return


def _gen_fooddata_json_path_and_name():
    """
    FoodDataテーブルの元となるjsonファイルの「フォルダpath」「ファイル名」を取得し、グローバル変数に書き込む。
    """
    global FOODDATA_JSON_PATH
    global FOODDATA_JSON_FILENAME
    FOODDATA_JSON_PATH = os.path.join(ROOT_PATH, "data")
    FOODDATA_JSON_FILENAME = "fooddata.json"
    return


def _gen_db_path_and_name(user_id):
    """
    SQLiteDBファイルの「フォルダpath」「ファイル名」を取得し、グローバル変数に書き込む。
    【補足】    複数のユーザーが本システムを用いるとき、SQLite-DBの.dbファイル等はユーザー等に別々に保存したい。
               そのため、ユーザーIDという概念を導入し、.db等はユーザーごとのフォルダ内に格納されるようにする。
    """
    global DB_PATH
    global DB_FILENAME
    global DB_BACKUP_FILENAME
    DB_PATH = os.path.join(ROOT_PATH, "data", "users", user_id)
    DB_FILENAME = "cooking_system.db"
    DB_BACKUP_FILENAME = "cooking_system_backup.db"
    return


def _memorize_user_id(user_id):
    """
    ユーザーIDをグローバル変数に記憶する。
    """
    global USER_ID
    # 念のためスペースをユーザーIDに変換する
    user_id = str(user_id)
    USER_ID = user_id.replace(" ", "_")
    return


# ________________________________________________________________________________________________________________________
if __name__ == "__main__":
    """
    中身閲覧用
    """
    init()
    print(f"ROOT_PATH              = {ROOT_PATH}")
    print(f"DB_PATH                = {DB_PATH}")
    print(f"DB_FILENAME            = {DB_FILENAME}")
    print(f"FOODDATA_JSON_PATH     = {FOODDATA_JSON_PATH}")
    print(f"FOODDATA_JSON_FILENAME = {FOODDATA_JSON_FILENAME}")
    print(f"USER_ID                = {USER_ID}")
    print(f"INIT_FINISH            = {INIT_FINISH}")
