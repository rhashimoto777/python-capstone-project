from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src import translator
from src.backend_app import save_user_selection as tmp_json_tool

user_food_select = None


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

    # データフレーム内の'FoodName'列に含まれる食材名のうち、重複しないものがリスト形式で格納
    food_options = df_fooddata["FoodName"].unique().tolist()
    # 食材を複数選択
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("食材を選んでください")
    with col2:
        # 前回選択内容をロードする。また、選択内容を消去するボタンを表示する。
        last_select = tmp_json_tool.restore("choice_food")
        default_food_sel = None
        default_quantity_sel = None

        if last_select is not None:
            if len(last_select["FoodName"]) > 0 or len(last_select["Quantity"]) > 0:
                bt_restore = st.button("選択内容を消去", key="cho_foo_res_last_sel")
                if not bt_restore:
                    default_food_sel = last_select["FoodName"]
                    default_quantity_sel = last_select["Quantity"]
                else:
                    default_food_sel = None
                    default_quantity_sel = None

    selected_foods = []
    col1, col2 = st.columns(2)
    with col1:
        # 食材の選択
        selected_foods = st.multiselect(
            "", food_options, default_food_sel, label_visibility="collapsed"
        )

        # 食材に対する数量を入力
        user_food_select = []
        total_kcal = 0
        total_protein = 0
        total_fat = 0
        total_carbs = 0

        # 前回選択内容を保存するためのリスト
        quantity_list = []

        for food_name in selected_foods:
            # データの取得
            map = df_fooddata["FoodName"] == food_name
            dict = {}
            dict["f_name"] = food_name
            dict["f_id"] = df_fooddata.loc[map, "FoodDataID"].values[0]
            dict["f_su_name"] = df_fooddata.loc[map, "StandardUnit_Name"].values[0]
            dict["f_su_g"] = df_fooddata.loc[map, "StandardUnit_Grams"].values[0]

            # 食材個数の入力のためのデフォルト値を生成（前回選択内容をロード）
            default_value = 1.0
            if default_food_sel is not None:
                for j, d_food in enumerate(default_food_sel):
                    if food_name == d_food:
                        default_value = default_quantity_sel[j]
                        break

            # 食材個数を入力
            msg = f'{food_name}の個数({dict["f_su_name"]})を入力してください'
            quantity = st.number_input(
                msg,
                min_value=0.0,
                value=default_value,
                step=0.1,
                label_visibility="collapsed",
            )

            # 前回選択内容をリストに保存
            quantity_list.append(quantity)

            # 選択内容からデータ変換
            dict["su_quantity"] = quantity
            dict["g"] = quantity * dict["f_su_g"]

            # 合計を計算
            total_kcal += quantity * df_fooddata.loc[map, "Calory_Total"].values[0]
            total_protein += quantity * df_fooddata.loc[map, "Grams_Protein"].values[0]
            total_fat += quantity * df_fooddata.loc[map, "Grams_Fat"].values[0]
            total_carbs += quantity * df_fooddata.loc[map, "Grams_Carbo"].values[0]

            user_food_select.append(dict)

        # jsonに選択内容を保存
        tmp_json_tool.save(
            key="choice_food",
            data={"FoodName": selected_foods, "Quantity": quantity_list},
        )
    with col2:
        if len(selected_foods) > 0:
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


def show_nutrition_info_of_cooking(unique_id):
    """
    JIRAチケット「PCPG-13」に対応する、
    『CookingIDごとの「料理の総カロリー」、「PFCそれぞれのグラム量」、「PFCそれぞれのカロリー量」』
    に相当する情報の取得方法とデータ利用方法についてのデモ。
    """
    cooking_info_list = translator.get_cooking_info_list()

    # タイトル
    # st.header("食材とPFCバランス")

    for i, ck in enumerate(cooking_info_list.cookings):
        st.subheader(f"No.{ck.cooking_id} : {ck.cooking_name}")

        # DataFrameの作成
        food_quantity = []
        for food in ck.food_attribute:
            food_quantity.append(
                {
                    "食材名": food.food_name,
                    "グラム数": food.grams_total,
                    "数量": f"{food.standard_unit_name} * 【{food.standard_unit_numbers:.1f}】",
                }
            )
        food_quantity = pd.DataFrame(food_quantity)

        food_calory = []
        for food in ck.food_attribute:
            food_calory.append(
                {
                    "食材名": food.food_name,
                    "Total": food.calory_total,
                    "Protein": food.caloty_protein,
                    "Fat": food.caloty_fat,
                    "Carbohydrate": food.caloty_carbo,
                }
            )
        food_calory = pd.DataFrame(food_calory)

        # 表示
        col1, col2 = st.columns(2)
        with col1:
            # st.dataframe(cooking_attribute)
            st.markdown(
                f"""
                - 【合計カロリー】{ck.calory_total:.1f}kcal
                - 【タンパク質(Protein)】{ck.caloty_protein:.1f}kcal ({ck.grams_protein:.1f}g)
                - 【脂質(Fat)】{ck.caloty_fat:.1f}kcal ({ck.grams_fat:.1f}g)
                - 【炭水化物(Carbohydrate)】{ck.caloty_carbo:.1f}kcal ({ck.grams_carbo:.1f}g)
            """
            )
            button1 = st.button(
                "使用する食材と量",
                key=f"show_nutrition_info_of_cooking_button1_{i}_{unique_id}",
            )
            if button1:
                st.dataframe(food_quantity)

            # with st.expander("食材ごとのカロリー", expanded=False):
            button2 = st.button(
                "食材ごとのカロリー",
                key=f"show_nutrition_info_of_cooking_button2_{i}_{unique_id}",
            )
            if button2:
                st.caption("単位は[kcal]")
                st.dataframe(food_calory)

        with col2:
            if ck.calory_total != 0:
                # PFCバランスの計算
                percentages = {
                    "Protein": ck.caloty_protein,
                    "Fat": ck.caloty_fat,
                    "Carbohydrate": ck.grams_carbo,
                }

                # ラベルと値のリスト化
                labels = list(percentages.keys())
                values = list(percentages.values())

                # 円グラフの作成
                fig = px.pie(
                    values=values,
                    names=labels,
                    title=f"PFCのカロリー比率 ({ck.cooking_name})",
                )

                #  円グラフの表示
                st.plotly_chart(fig)
            else:
                st.caption("合計カロリーがゼロ")

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
    show_nutrition_info_of_cooking("scr")
    return
