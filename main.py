import sys
import os

# subfolderをモジュール検索パスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
subfolder_path = os.path.join(current_dir, 'src')
sys.path.insert(0, subfolder_path)

# srcフォルダ内の.pyをインポート
import frontend_main

import translator
import backend_main

#________________________________________________________________________________________________________________________
def main():
    """
    メイン処理
    """
    frontend_op = frontend_main.FrontEndOperator()
    frontend_op.run()
    
#________________________________________________________________________________________________________________________
if __name__ == "__main__":
    main()