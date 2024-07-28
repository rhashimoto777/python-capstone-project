import os
from pathlib import Path

ROOT_PATH = ""
DB_PATH = ""
DB_FILENAME = ""
FOODDATA_JSON_PATH = ""
FOODDATA_JSON_FILENAME = ""

def init(user_id = 'user_default'):
    """
    初回起動時の処理
    """
    _gen_root_path()
    _gen_fooddata_json_path_and_name()
    _gen_db_path_and_name(user_id)

def _gen_root_path():
    """
    最上位フォルダ (main.pyがあるフォルダ) のpathを取得し、グローバル変数に書き込む。
    """
    global ROOT_PATH
    current_path = Path(__file__).resolve().parent
    ROOT_PATH = current_path.parent
    return

def _gen_fooddata_json_path_and_name():
    global FOODDATA_JSON_PATH
    global FOODDATA_JSON_FILENAME
    FOODDATA_JSON_PATH = f'{ROOT_PATH}/data'
    FOODDATA_JSON_FILENAME = 'fooddata.json'
    return

def _gen_db_path_and_name(user_id):
    """
    (1) システム内でDBのpath・ファイルが確実に一意になるよう、事前に生成する。
    (2) 複数のユーザーが本システムを用いるとき、SQLite-DBの.dbファイル等はユーザー等に別々に保存したい。
        そのため、ユーザーIDという概念を導入し、.db等はユーザーごとのフォルダ内に格納されるようにする。
    """
    global DB_PATH
    global DB_FILENAME
    DB_PATH = f'{ROOT_PATH}/data/{user_id}'
    DB_FILENAME = 'cooking_system.db'
    return

if __name__ == "__main__":
    init()
    print(f'ROOT_PATH              = {ROOT_PATH}')
    print(f'DB_PATH                = {DB_PATH}')
    print(f'DB_FILENAME            = {DB_FILENAME}')
    print(f'FOODDATA_JSON_PATH     = {FOODDATA_JSON_PATH}')
    print(f'FOODDATA_JSON_FILENAME = {FOODDATA_JSON_FILENAME}')