import sys
import os

# subfolderをモジュール検索パスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
subfolder_path = os.path.join(current_dir, 'src')
sys.path.insert(0, subfolder_path)

# srcフォルダ内の.pyをインポート
import sqlite3_db
import common

#________________________________________________________________________________________________________________________
def init_process():
    """
    初回起動時の処理
    """
    # ユーザーIDの概念は今後の拡張に備えたものであり、現実装においては「user_default」以外のユーザーは存在しないとする。
    common.init() 
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