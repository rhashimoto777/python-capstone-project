import sys
import os

# subfolderをモジュール検索パスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
subfolder_path = os.path.join(current_dir, 'backend_app')
sys.path.insert(0, subfolder_path)

# back-end_appフォルダ内の.pyをインポート
import sqlite3_db
import backend_common as common
import fooddata

class BackEndMain():
    def __init__(self):
        pass


#________________________________________________________________________________________________________________________
def init_process():
    """
    初回起動時の処理
    """
    common.init() 
    fooddata.init()
    sqlite3_db.init()

def main():
    """
    メイン処理
    """
    pass
    
#________________________________________________________________________________________________________________________
if __name__ == "__main__":
    init_process()
    main()