import sys
import os

# subfolderをモジュール検索パスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
subfolder_path = os.path.join(current_dir, 'backend_app')
sys.path.insert(0, subfolder_path)

# backend_appフォルダ内の.pyをインポート
import sqlite_db
import fooddata
import backend_common as common

#________________________________________________________________________________________________________________________
class BackEndOperator():
    def __init__(self):
        common.init() 
        fooddata.init()
        db_operator = sqlite_db.DataBaseOperator()

#________________________________________________________________________________________________________________________
if __name__ == "__main__":
    # (デバッグ用)
    backend = BackEndOperator()