import streamlit as st
import pandas as pd
import translator
import plotly.express as px
import plotly.graph_objects as go

# デバッグ表示モード
IS_DEBUG_PRINT_MODE_IN_FRONTEND = True

#________________________________________________________________________________________________________________________
class FrontEndOperator():
    def __init__(self) -> None:
        self.translator = translator.Translator()
        return
    
    def run(self):
        self.__show_cookings_registered()
        self.__show_refrigerator_fooddata()
        self.__resister_cooking()
        self.__start_cooking()
        self.__show_nutrition_info_of_cooking()
            
    def __show_cookings_registered(self):
        """
        既に登録済みの料理を表示する。
        """
        df_cooking = self.translator.get_df_cooking()
        st.title('登録済みの料理')
        st.caption('「Cooking」内にある食材の情報を、UI上に表示する。')
        st.dataframe(df_cooking)
    
    def __show_refrigerator_fooddata(self):
        df_refrigerator = self.translator.get_df_refrigerator()
        df_fooddata = self.translator.get_df_fooddata()
        
        # Streamlitを使ってDataFrameを表示
        st.title('冷蔵庫の中にある食材の種類・数')
        st.caption('「Refrigerator」内にある食材の情報を、「Refrigerator」」と「FoodData」のDataframeを参照して、UI上に表示する。')
        df_refrigerator_fooddata = df_refrigerator.merge(df_fooddata, on='FoodDataID')
        st.dataframe(df_refrigerator_fooddata[["FoodDataID", "FoodName", "Grams"]])
        return

    def __resister_cooking(self):
        df_fooddata = self.translator.get_df_fooddata()
        # Streamlitを使って食材選択をスライドバー表示
        st.sidebar.title("使う食材と数量を選択")
        # データフレーム内の'FoodName'列に含まれる食材名のうち、重複しないものがリスト形式で格納
        food_options = df_fooddata['FoodName'].unique().tolist()
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

        # 料理名を登録
        name = st.sidebar.text_input('新しい料理の料理名を教えてください')

        # 日付入力
        date = st.sidebar.date_input('Input date')
       
        # ボタン
        register_btn = st.sidebar.button('料理を登録')
        return

    def __start_cooking(self):
        """
        「料理を作る」ボタンを押すと「cooking_id」が生成され、backend_op.add_cooking_historyを呼び出す。
        """
        ####### データの準備 ######
        df_cooking = self.translator.get_df_cooking()

        ####### ユーザー操作 ######
        st.sidebar.title("料理を作る")
        user_input_cookingid = st.sidebar.text_input('登録済みの料理からCookingIDを入力してください')
        cooking_button = st.sidebar.button('料理を作る', key='button2')

        ####### データ処理 ######
        # ユーザーが入力したCookingIDが整数かどうかを検証
        try:
            cooking_id = int(user_input_cookingid)  # 入力を整数に変換
        except ValueError:
            cooking_id = None  # 整数でない場合はNoneを設定
        
        # ボタンがクリックされたときの挙動
        if cooking_button:
            if cooking_id is not None:
                # `cooking_id` が `cooking` テーブルの `CookingID` 列に存在するか確認
                if cooking_id in df_cooking['CookingID'].values:
                    # 存在する場合、料理の履歴を追加
                    self.translator.add_cooking_history(cooking_id)
                    st.sidebar.success('料理の履歴が追加されました。')
                else:
                    # 存在しない場合、エラーメッセージを表示
                    st.sidebar.error('指定されたCookingIDは登録されていません。')
            else:
                # 整数でない入力に対するエラーメッセージ
                st.sidebar.error('無効な入力です！整数を入力してください。')
        return
    

    def __show_nutrition_info_of_cooking(self):
        """
        JIRAチケット「PCPG-13」に対応する、
        『CookingIDごとの「料理の総カロリー」、「PFCそれぞれのグラム量」、「PFCそれぞれのカロリー量」』
        に相当する情報の取得方法とデータ利用方法についてのデモ。
        """
        cooking_details = self.translator.get_cooking_details()

        # タイトル
        st.title("料理ごとのカロリーとPFCバランス")

        for cooking_details_elem in cooking_details:
            cooking_id = cooking_details_elem["CookingID"] 
            cooking_attribute = cooking_details_elem["CookingAttribute"]
            food_attribute = cooking_details_elem["FoodAttribute"]

            cooking_name = cooking_attribute["CookingName"].values[0]

            st.subheader(f'{cooking_id} : {cooking_name}')
            st.write(cooking_attribute)

            #各カロリーの取得
            total_calories = float(cooking_attribute["CookingCalory_Total"])
            protein_calories = float(cooking_attribute["CookingCalory_Protein"])
            fat_calories = float(cooking_attribute["CookingCalory_Fat"])
            carbo_calories = float(cooking_attribute["CookingCalory_Carbo"])

            #PFCバランスの計算
            percentages = {
                "Protein": (protein_calories / total_calories) * 100,
                "Fat": (fat_calories / total_calories) * 100,
                "Carbohydrate": (carbo_calories / total_calories) * 100
                }

            # ラベルと値のリスト化
            labels = list(percentages.keys())
            values = list(percentages.values())

            # 円グラフの作成
            fig = px.pie(values=values, names=labels, title=f'PFCバランス (CookingID: {cooking_id})')

            #  円グラフの表示
            st.plotly_chart(fig)
            st.write(f"Total Calories: {total_calories} kcal") 



def debug_print(d, message):
    if IS_DEBUG_PRINT_MODE_IN_FRONTEND:
        print(f'==============[Front-end] (DEBUG PRINT) {message}==============')
        print(d)
    return

def system_msg_print(msg):
    """
    Frontend側で用いるシステムメッセージ表示用のprint関数
    """
    print(f'[frontend : system-message] {msg}')
    return