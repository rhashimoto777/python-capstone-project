import sys
import os
import streamlit as st

# subfolderをモジュール検索パスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
subfolder_path = os.path.join(current_dir, 'frontend_app')
sys.path.insert(0, subfolder_path)

# frontend_appフォルダ内の.pyをインポート
import frontend_common as common

#________________________________________________________________________________________________________________________
class FrontEndOperator():
    def __init__(self, initial_df_dict) -> None:
        self.df_dict = initial_df_dict
        return

    def update_df_dict(self, df_dict):
        self.df_dict = df_dict
        return
    
    def sample_show_all_df(self):
        table_name_list = list(self.df_dict.keys())
        for table in table_name_list:
            st.header(f"Table: {table}")
            df = self.df_dict[table]
            st.dataframe(df)
