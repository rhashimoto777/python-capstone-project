import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from src import translator

def main_page():
    resister_cooking()
    start_cooking()
    show_cookings_registered()
    show_refrigerator_fooddata()
    show_nutrition_info_of_cooking()
    return
        
def show_cookings_registered():
    """
    既に登録済みの料理を表示する。
    """
    df_cooking = translator.get_df_cooking()
    st.title('登録済みの料理')
    st.caption('「Cooking」内にある食材の情報を、UI上に表示する。')
    st.dataframe(df_cooking)
    return

def show_refrigerator_fooddata():
    df_refrigerator = translator.get_df_refrigerator()
    df_fooddata = translator.get_df_fooddata()
    
    # Streamlitを使ってDataFrameを表示
    st.title('冷蔵庫の中にある食材の種類・数')
    st.caption('「Refrigerator」内にある食材の情報を、「Refrigerator」」と「FoodData」のDataframeを参照して、UI上に表示する。')
    df_refrigerator_fooddata = df_refrigerator.merge(df_fooddata, on='FoodDataID')
    st.dataframe(df_refrigerator_fooddata[["FoodDataID", "FoodName", "Grams"]])
    return

def resister_cooking():
    df_fooddata = translator.get_df_fooddata()
    # Streamlitを使って食材選択をスライドバー表示
    st.sidebar.title("使う食材と数量を選択")
    # データフレーム内の'FoodName'列に含まれる食材名のうち、重複しないものがリスト形式で格納
    food_options = df_fooddata['FoodName'].unique().tolist()
    # 食材を複数選択
    selected_foods = st.sidebar.multiselect("食材を選んでください", food_options)
    
    # 食材に対する数量を入力
    user_food_select = []
    total_kcal = 0
    total_protein = 0
    total_fat = 0
    total_carbs = 0

    for food_name in selected_foods:
        map = df_fooddata['FoodName'] == food_name
        dict = {}
        dict["f_name"]      = food_name
        dict["f_id"]        = df_fooddata.loc[map, 'FoodDataID'].values[0]
        dict["f_su_name"]   = df_fooddata.loc[map, 'StandardUnit_Name'].values[0]
        dict["f_su_g"]      = df_fooddata.loc[map, 'StandardUnit_Grams'].values[0]

        msg = f'{food_name}の個数({dict["f_su_name"]})を入力してください'
        quantity = st.sidebar.number_input(msg, min_value=0, value=1)
        dict["su_quantity"] = quantity
        dict["g"]           = quantity * dict["f_su_g"]

        # 合計を計算
        total_kcal += quantity * df_fooddata.loc[map, 'Calory_Total'].values[0]
        total_protein += quantity * df_fooddata.loc[map, 'Grams_Protein'].values[0]
        total_fat += quantity * df_fooddata.loc[map, 'Grams_Fat'].values[0]
        total_carbs += quantity * df_fooddata.loc[map, 'Grams_Carbo'].values[0]
    
        user_food_select.append(dict)

    # 選択した食材と個数を表示
    st.sidebar.write("選択した食材と個数を確認:")
    for food in user_food_select:
        msg = f'{food["f_name"]}: {food["f_su_name"]} * {food["su_quantity"]} ({food["g"]}g)'
        st.sidebar.write(msg)

    # 料理を編集中の画面でも、編集中の料理の総カロリー等を表示する
    # 合計値を表示
    st.sidebar.write("選択した食材の総カロリー:")
    st.sidebar.write(f"総カロリー: {total_kcal:.2f} kcal")
    st.sidebar.write(f"総タンパク質: {total_protein:.2f} g")
    st.sidebar.write(f"総脂質: {total_fat:.2f} g")
    st.sidebar.write(f"総炭水化物: {total_carbs:.2f} g")

    # # PFCバランスの円グラフを作成
    fig = go.Figure(data=[go.Pie(labels=['タンパク質', '脂質', '炭水化物'],
                                    values=[total_protein, total_fat, total_carbs],
                                    textinfo='label+percent')])
    st.sidebar.write("PFCバランス:")
    st.sidebar.plotly_chart(fig)

    # 料理名・説明・お気に入り登録
    c_name = st.sidebar.text_input('新しい料理の料理名を教えてください')
    c_desc = st.sidebar.text_area('説明')
    is_favorite = st.sidebar.toggle("お気に入り登録")

    # 登録ボタン
    register_btn = st.sidebar.button('料理を登録')
    if register_btn:
        dict = []
        for food in user_food_select:
            dict.append({"FoodDataID":food["f_id"], "Grams":food["g"]})
        df_food_and_grams = pd.DataFrame(dict)

        dict = []
        dict.append({"CookingName":c_name, "isFavorite":is_favorite, "LastUpdateDate":datetime.now(), "Description":c_desc})
        df_cooking_attributes = pd.DataFrame(dict)
        is_success, msg = translator.add_cooking(df_food_and_grams, df_cooking_attributes)
        if is_success:
            st.sidebar.success('料理を追加しました')
        else:
            if msg == "same_cooking_already_exist":
                st.sidebar.error('同じ材料構成の料理が既に登録されています')
            else:
                st.sidebar.error('料理の追加に失敗しました')
    return

def start_cooking():
    """
    「料理を作る」ボタンを押すと「cooking_id」が生成され、backend_op.add_cooking_historyを呼び出す。
    """
    ####### データの準備 ######
    df_cooking = translator.get_df_cooking()

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
                translator.add_cooking_history(cooking_id)
                st.sidebar.success('料理の履歴が追加されました。')
            else:
                # 存在しない場合、エラーメッセージを表示
                st.sidebar.error('指定されたCookingIDは登録されていません。')
        else:
            # 整数でない入力に対するエラーメッセージ
            st.sidebar.error('無効な入力です！整数を入力してください。')
    return


def show_nutrition_info_of_cooking():
    """
    JIRAチケット「PCPG-13」に対応する、
    『CookingIDごとの「料理の総カロリー」、「PFCそれぞれのグラム量」、「PFCそれぞれのカロリー量」』
    に相当する情報の取得方法とデータ利用方法についてのデモ。
    """
    cooking_details = translator.get_cooking_details()

    # タイトル
    st.title("料理ごとのカロリーとPFCバランス")

    for cooking_details_elem in cooking_details:
        cooking_id = cooking_details_elem["CookingID"] 
        cooking_attribute = cooking_details_elem["CookingAttribute"]
        food_attribute = cooking_details_elem["FoodAttribute"]

        cooking_name = cooking_attribute["CookingName"].values[0]

        st.subheader(f'{cooking_id} : {cooking_name}')
        st.write(cooking_attribute)
        st.table(food_attribute)

        #各カロリーの取得
        total_calories = float(cooking_attribute["CookingCalory_Total"].values[0])
        protein_calories = float(cooking_attribute["CookingCalory_Protein"].values[0])
        fat_calories = float(cooking_attribute["CookingCalory_Fat"].values[0])
        carbo_calories = float(cooking_attribute["CookingCalory_Carbo"].values[0])

        if total_calories != 0:
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
    return