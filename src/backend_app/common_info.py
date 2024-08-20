import os
from pathlib import Path

from src import util

# バックエンド内で参照するpath・ファイル名
ROOT_DIR = None
USER_LIST_DIR = None
CURRENT_USER_FILE_DIR = None
CURRENT_USER_FILENAME = None
DB_DIR = None
DB_FILENAME = None
DB_BACKUP_FILENAME = None
FOODDATA_JSON_DIR = None
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
        util.backend_system_msg(
            f"********** common_info init (user_id = {user_id}) **********"
        )
        update(user_id)
    else:
        pass
    return


def update(user_id="user_default"):
    global USER_ID, INIT_FINISH
    if user_id == USER_ID:
        return
    if not INIT_FINISH:
        util.backend_system_msg(
            f"********** common_info update (user_id = {user_id}) **********"
        )

    _memorize_user_id(user_id)
    _gen_root_path()
    _gen_fooddata_json_path_and_name()
    _gen_db_user_path_and_name(user_id)
    INIT_FINISH = True
    return


# ________________________________________________________________________________________________________________________
# private関数


def _gen_root_path():
    """
    最上位フォルダ (main.pyがあるフォルダ) のpathを取得し、グローバル変数に書き込む。
    """
    global ROOT_DIR
    current_path = Path(__file__).resolve().parent
    ROOT_DIR = current_path.parent.parent
    return


def _gen_fooddata_json_path_and_name():
    """
    FoodDataテーブルの元となるjsonファイルの「フォルダpath」「ファイル名」を取得し、グローバル変数に書き込む。
    """
    global FOODDATA_JSON_DIR
    global FOODDATA_JSON_FILENAME
    FOODDATA_JSON_DIR = os.path.join(ROOT_DIR, "data")
    FOODDATA_JSON_FILENAME = "fooddata.json"
    return


def _gen_db_user_path_and_name(user_id):
    """
    SQLiteDBファイルの「フォルダpath」「ファイル名」を取得し、グローバル変数に書き込む。
    【補足】    複数のユーザーが本システムを用いるとき、SQLite-DBの.dbファイル等はユーザー等に別々に保存したい。
               そのため、ユーザーIDという概念を導入し、.db等はユーザーごとのフォルダ内に格納されるようにする。
    """
    global USER_LIST_DIR
    global CURRENT_USER_FILE_DIR
    global CURRENT_USER_FILENAME
    global DB_DIR
    global DB_FILENAME
    global DB_BACKUP_FILENAME

    CURRENT_USER_FILE_DIR = os.path.join(ROOT_DIR, "data")
    CURRENT_USER_FILENAME = "current_user.txt"

    USER_LIST_DIR = os.path.join(ROOT_DIR, "data", "users")
    DB_DIR = os.path.join(USER_LIST_DIR, user_id)
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
