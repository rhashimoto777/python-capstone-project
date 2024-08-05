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

        # Streamlitを使って食材選択をスライドバー表示
        st.sidebar.title("使う食材と数量を選択")
        # データフレーム内の'FoodName'列に含まれる食材名のうち、重複しないものがリスト形式で格納
        food_options = df_dict_refrigerator_fooddata['FoodName'].unique().tolist()
        # 食材を複数選択
        selected_foods = st.sidebar.multiselect("食材を選んでください", food_options)
        
        # 食材に対する数量を入力
        selected_quantities = {}
        for food in selected_foods:
            quantity = st.sidebar.number_input(f"{food}の重量(g)を入力してください", min_value=0, value=1)
            selected_quantities[food] = quantity

        # 選択した食材と個数を表示
        st.sidebar.write("選択した食材と重量(g)を確認:")
        for food, quantity in selected_quantities.items():
            st.sidebar.write(f"{food}: {quantity}")

        #料理名を登録
        text = st.sidebar.text_input('新しい料理の料理名を教えてください')

        # 日付入力
        date = st.sidebar.date_input('Input date')
       
        # ボタン
        st.sidebar.button('料理を登録')

        return

