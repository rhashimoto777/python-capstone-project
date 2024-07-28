from pathlib import Path
import os

# デバッグ表示モード
IS_DEBUG_PRINT_MODE_IN_BACKEND = True

# バックエンド内で参照するpath・ファイル名
ROOT_PATH = None
DB_PATH = None
DB_FILENAME = None
FOODDATA_JSON_PATH = None
FOODDATA_JSON_FILENAME = None

#________________________________________________________________________________________________________________________
# global関数

def init(user_id = 'user_default'):
    """
    初回起動時の処理
    """
    _gen_root_path()
    _gen_fooddata_json_path_and_name()
    _gen_db_path_and_name(user_id)

def debug_print(d, message):
    if IS_DEBUG_PRINT_MODE_IN_BACKEND:
        print(f'==============[Back-end] (DEBUG PRINT) {message}==============')
        print(d)
    return

#________________________________________________________________________________________________________________________
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
    FOODDATA_JSON_PATH = os.path.join(ROOT_PATH, 'data')
    FOODDATA_JSON_FILENAME = 'fooddata.json'
    return

def _gen_db_path_and_name(user_id):
    """
    SQLiteDBファイルの「フォルダpath」「ファイル名」を取得し、グローバル変数に書き込む。
    【補足】    複数のユーザーが本システムを用いるとき、SQLite-DBの.dbファイル等はユーザー等に別々に保存したい。
               そのため、ユーザーIDという概念を導入し、.db等はユーザーごとのフォルダ内に格納されるようにする。
    """
    global DB_PATH
    global DB_FILENAME
    DB_PATH = os.path.join(ROOT_PATH, 'data', user_id)
    DB_FILENAME = 'cooking_system.db'
    return

#________________________________________________________________________________________________________________________
if __name__ == "__main__":
    init()
    print(f'ROOT_PATH              = {ROOT_PATH}')
    print(f'DB_PATH                = {DB_PATH}')
    print(f'DB_FILENAME            = {DB_FILENAME}')
    print(f'FOODDATA_JSON_PATH     = {FOODDATA_JSON_PATH}')
    print(f'FOODDATA_JSON_FILENAME = {FOODDATA_JSON_FILENAME}')