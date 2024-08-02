import sys
import os
import streamlit as st
import pandas as pd

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

class FrontEndOperatorRefrigeratorFooddata():
    def __init__(self, initial_df_dict, second_df_dict) -> None:
        self.df_dict1 = initial_df_dict
        self.df_dict2 = second_df_dict
        return

    def update_df_dict(self, df_dict1, df_dict2):
        self.df_dict1 = df_dict1
        self.df_dict2 = df_dict2
        return
    
    def show_refrigerator_fooddata_df(self, df_dict_refrigerator, df_dict_fooddata) :
        
        # Streamlitを使ってDataFrameを表示
        st.title('冷蔵庫の中にある食材の種類・数')
        st.caption('「Refrigerator」内にある食材の情報を、「Refrigerator」」と「FoodData」のDataframeを参照して、UI上に表示する。')
        df_dict_refrigerator_fooddata = pd.merge(df_dict_refrigerator, df_dict_fooddata, how='inner')
        st.dataframe(df_dict_refrigerator_fooddata)
        return



