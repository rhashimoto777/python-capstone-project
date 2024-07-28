import sys
import os
import streamlit as st

# subfolderをモジュール検索パスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
subfolder_path = os.path.join(current_dir, 'src')
sys.path.insert(0, subfolder_path)

# srcフォルダ内の.pyをインポート
import backend_main
import frontend_main

#________________________________________________________________________________________________________________________
def main():
    """
    メイン処理
    """
    backend_op = backend_main.BackEndOperator()
    df_dict = backend_op.get_df_from_db()
    
    frontend_op = frontend_main.FrontEndOperator(df_dict)
    frontend_op.sample_show_all_df()
    
#________________________________________________________________________________________________________________________
if __name__ == "__main__":
    main()