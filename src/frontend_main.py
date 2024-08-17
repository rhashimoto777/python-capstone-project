from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src import translator

user_food_select = None


def main_page():
    resister_cooking()
    start_cooking()
    show_cookings_registered()
    show_refrigerator_fooddata()
    show_nutrition_info_of_cooking()
    show_cookinghistory_registered()
    return


def show_cookings_registered():
    """
    既に登録済みの料理を表示する。
    """
    df_cooking = translator.get_df_cooking()
    # LastUpdateDateをdatetime型に変換してから分までにフォーマット
    df_cooking["LastUpdateDate"] = pd.to_datetime(
        df_cooking["LastUpdateDate"]
    ).dt.strftime("%Y-%m-%d %H:%M")

    # カラムの順序を変更
    df_cooking = df_cooking[
        ["CookingID", "CookingName", "IsFavorite", "LastUpdateDate", "Description"]
    ]

    st.subheader("登録済みの料理リスト")
    # st.caption('「Cooking」内にある食材の情報を、UI上に表示する。')
    # データフレームをHTML形式に変換し、インデックスを非表示にする
    html = df_cooking.to_html(index=False, justify="left")

    # HTMLで表示
    st.markdown(html, unsafe_allow_html=True)
    return


def show_refrigerator_fooddata():
    df_refrigerator = translator.get_df_refrigerator()
    df_fooddata = translator.get_df_fooddata()

    # Streamlitを使ってDataFrameを表示
    st.subheader("冷蔵庫の食材と数量")
    # st.caption('「Refrigerator」内にある食材の情報を、「Refrigerator」」と「FoodData」のDataframeを参照して、UI上に表示する。')
    df_refrigerator_fooddata = df_refrigerator.merge(df_fooddata, on="FoodDataID")
    # HTMLでデータフレームを表示
    html = df_refrigerator_fooddata[["FoodName", "Grams"]].to_html(
        index=False, justify="left"
    )
    st.markdown(html, unsafe_allow_html=True)
    return


def choice_food():
    global user_food_select
    df_fooddata = translator.get_df_fooddata()
    # Streamlitを使って食材選択を表示
    # st.header("【使う食材と数量を選択】")
    # データフレーム内の'FoodName'列に含まれる食材名のうち、重複しないものがリスト形式で格納
    food_options = df_fooddata["FoodName"].unique().tolist()
    # 食材を複数選択
    st.subheader("食材を選んでください")
    col1, col2 = st.columns(2)
    with col1:
        selected_foods = st.multiselect("", food_options)

        # 食材に対する数量を入力
        user_food_select = []
        total_kcal = 0
        total_protein = 0
        total_fat = 0
        total_carbs = 0

        for food_name in selected_foods:
            map = df_fooddata["FoodName"] == food_name
            dict = {}
            dict["f_name"] = food_name
            dict["f_id"] = df_fooddata.loc[map, "FoodDataID"].values[0]
            dict["f_su_name"] = df_fooddata.loc[map, "StandardUnit_Name"].values[0]
            dict["f_su_g"] = df_fooddata.loc[map, "StandardUnit_Grams"].values[0]

            msg = f'{food_name}の個数({dict["f_su_name"]})を入力してください'
            quantity = st.number_input(msg, min_value=0.0, value=1.0, step=0.1)

            dict["su_quantity"] = quantity
            dict["g"] = quantity * dict["f_su_g"]

            # 合計を計算
            total_kcal += quantity * df_fooddata.loc[map, "Calory_Total"].values[0]
            total_protein += quantity * df_fooddata.loc[map, "Grams_Protein"].values[0]
            total_fat += quantity * df_fooddata.loc[map, "Grams_Fat"].values[0]
            total_carbs += quantity * df_fooddata.loc[map, "Grams_Carbo"].values[0]

            user_food_select.append(dict)

        ## 選択した食材と個数を表示
        ## st.write("選択した食材と個数を確認:")
        ## for food in user_food_select:
        ##     msg = f'{food["f_name"]}: {food["f_su_name"]} * {food["su_quantity"]} ({food["g"]}g)'
        ##     st.write(msg)

        ## 料理を編集中の画面でも、編集中の料理の総カロリー等を表示する
        ## 合計値を表示
        ## st.write("選択した食材の総カロリー:")
    with col2:

        ## st.write(f"総タンパク質: {total_protein:.2f} g")
        ## st.write(f"総脂質: {total_fat:.2f} g")
        ## st.write(f"総炭水化物: {total_carbs:.2f} g")

        # # PFCバランスの円グラフを作成
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=["タンパク質", "脂質", "炭水化物"],
                    values=[total_protein, total_fat, total_carbs],
                    textinfo="label+percent",
                )
            ]
        )
        # st.write("PFCバランス:")
        st.plotly_chart(fig)
        st.write(f"総カロリー: {total_kcal:.2f} kcal")
        return


def resister_cooking():
    # 料理名・説明・お気に入り登録
    # st.header("【新しい料理を登録】")
    st.subheader("新しい料理の料理名を教えてください")
    c_name = st.text_input("")
    st.subheader("説明")
    c_desc = st.text_area("")
    st.subheader("お気に入り登録")
    is_favorite = st.toggle("")

    # 登録ボタン
    register_btn = st.button("料理を登録")
    if register_btn:
        food_attribute = []
        for food in user_food_select:
            f_elem = translator.gen_food_info(food_id=food["f_id"], grams=food["g"])
            food_attribute.append(f_elem)

        cooking_info = translator.gen_cooking_info(
            cooking_name=c_name,
            is_favorite=is_favorite,
            last_update_date=datetime.now(),
            description=c_desc,
            food_attr=food_attribute,
        )
        if translator.judge_is_new_cooking(cooking_info):
            try:
                translator.register_new_cooking(cooking_info)
                st.success("料理を追加しました")
                st.balloons()
            except Exception:
                st.error("料理の追加に失敗しました")
        else:
            st.error("同じ材料構成の料理が既に登録されています")
    return


def start_cooking():
    """
    「料理を作る」ボタンを押すと「cooking_id」が生成され、backend_op.add_cooking_historyを呼び出す。
    """
    ####### データの準備 ######
    df_cooking = translator.get_df_cooking()

    ####### ユーザー操作 ######
    # st.header('料理を作りましょう')
    # st.title("料理を作る")
    st.subheader("登録済みの料理からCookingIDを入力してください")
    user_input_cookingid = st.text_input("")
    cooking_button = st.button("料理を作る", key="button2")

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
            if cooking_id in df_cooking["CookingID"].values:
                # 存在する場合、料理の履歴を追加
                translator.add_cooking_history(cooking_id)
                st.success("料理の履歴が追加されました。")
                st.balloons()
            else:
                # 存在しない場合、エラーメッセージを表示
                st.error("指定されたCookingIDは登録されていません。")
        else:
            # 整数でない入力に対するエラーメッセージ
            st.error("無効な入力です！整数を入力してください。")
    return


def show_nutrition_info_of_cooking():
    """
    JIRAチケット「PCPG-13」に対応する、
    『CookingIDごとの「料理の総カロリー」、「PFCそれぞれのグラム量」、「PFCそれぞれのカロリー量」』
    に相当する情報の取得方法とデータ利用方法についてのデモ。
    """
    cooking_info_list = translator.get_cooking_info_list()

    # タイトル
    # st.header("食材とPFCバランス")

    for ck in cooking_info_list.cookings:
        st.subheader(f"{ck.cooking_id} : {ck.cooking_name}")
        # st.write(cooking_attribute)
        # st.table(food_attribute)

        if ck.calory_total != 0:
            # PFCバランスの計算
            percentages = {
                "Protein": (ck.caloty_protein / ck.calory_total) * 100,
                "Fat": (ck.caloty_fat / ck.calory_total) * 100,
                "Carbohydrate": (ck.grams_carbo / ck.calory_total) * 100,
            }

            # ラベルと値のリスト化
            labels = list(percentages.keys())
            values = list(percentages.values())

            # 円グラフの作成
            fig = px.pie(
                values=values,
                names=labels,
                title=f"PFCバランス (CookingID: {ck.cooking_id})",
            )

            #  円グラフの表示
        st.plotly_chart(fig)
        st.write(f"Total Calories: {ck.calory_total} kcal")
    return


def show_cookinghistory_registered():
    """
    過去に作った料理を表示する。
    """
    df_cookinghistory = translator.get_df_cookinghistory()
    df_cooking = translator.get_df_cooking()
    df_cookinghistory_cooking = df_cookinghistory.merge(df_cooking, on="CookingID")
    # st.title("過去に作った料理")
    # st.caption("「CookingHistory」内にある過去に作った料理を、UI上に表示する。")
    # st.dataframe(df_cookinghistory_cooking)

    # LastUpdateDateをdatetime型に変換してから分までにフォーマット
    df_cookinghistory_cooking["IssuedDate"] = pd.to_datetime(
        df_cookinghistory_cooking["IssuedDate"]
    ).dt.strftime("%Y-%m-%d %H:%M")

    # HTMLでデータフレームを表示
    html = df_cookinghistory_cooking[
        ["IssuedDate", "CookingName", "Description"]
    ].to_html(index=False, justify="left")
    st.markdown(html, unsafe_allow_html=True)

    """
    過去に作った料理ごとのカロリーとPFCバランス等を表示する。
    """

    st.subheader("過去に作った料理ごとのカロリーとPFCバランス")
    show_nutrition_info_of_cooking()
    return
