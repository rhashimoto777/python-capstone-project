import sys
import os
import streamlit as st
import pandas as pd
from datetime import datetime

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

    # <<< 説明用デモ1 >>>
    # sample_demo(backend_op, frontend_op)

    # <<< 説明用デモ2 >>>（とりあえずDataBaseの内容全てをブラウザに表示）
    # コメントアウトして、streamlit run main.py で実行できます。
    # frontend_op.sample_show_all_df() 

#________________________________________________________________________________________________________________________
def sample_demo(backend_op, frontend_op):
    """
    データの流れやIFの説明用のデモ関数です (実開発が軌道に乗ったら削除します)。
    主にフロントエンド側とバックエンド側を繋ぐIFや操作について説明します。
    """

    """
    使い勝手(1)：料理の登録（但し実際に作りはしない）

    - 「Cooking」には登録されるが、「CookingHistory」には登録されない。
        - 既にCookingに同じ組成の料理があれば、新しくCookingには登録されない。
    -  以下、例として「親子丼」を登録する。
        - 「df_food_and_grams」「df_cooking_attributes」の2つの入力を生成し、backend_op.add_cooking()を呼び出す。
        - これら2つの変数は本来はStreamLitのUI操作で生成するが、今回はサンプルとして直に生成する。
    """
    print("=========「使い勝手(1)のデモ」==========")
    print("### 操作前のDataBaseはこちら ###")
    df_dict = backend_op.get_df_from_db()
    print("【Cookingテーブル】")
    print(df_dict["Cooking"])
    print("【CookingFoodDataテーブル】")
    print(df_dict["CookingFoodData"])
    print("【CookingHistoryテーブル】")
    print(df_dict["CookingHistory"])

    ### フロントエンド側から得られる操作情報（＝バックエンド側への入力情報）を生成する。
    dict = []
    dict.append({"FoodDataID":0, "Grams":100}) # 鶏もも肉100g
    dict.append({"FoodDataID":1, "Grams":52})  # 卵1個
    dict.append({"FoodDataID":2, "Grams":94})  # 玉ねぎ1/2個
    dict.append({"FoodDataID":3, "Grams":90})  # 米0.5合
    dict.append({"FoodDataID":4, "Grams":12})  # サラダ油大さじ1
    dict.append({"FoodDataID":6, "Grams":18})  # 醤油大さじ1
    dict.append({"FoodDataID":7, "Grams":15})  # 料理酒大さじ1
    dict.append({"FoodDataID":8, "Grams":18})  # みりん大さじ1
    df_food_and_grams = pd.DataFrame(dict)

    dict = []
    dict.append({"CookingName":"親子丼", "isFavorite":True, "LastUpdateDate":datetime.now(), "Description":"定番の家庭の味"})
    df_cooking_attributes = pd.DataFrame(dict)

    ### 料理を登録する。
    backend_op.add_cooking(df_food_and_grams, df_cooking_attributes)

    ### 操作後のDataBaseはこちら
    print("### 操作後のDataBaseはこちら ###")
    df_dict = backend_op.get_df_from_db()
    print("【Cookingテーブル】")
    print(df_dict["Cooking"])
    print("【CookingFoodDataテーブル】")
    print(df_dict["CookingFoodData"])
    print("【CookingHistoryテーブル】")
    print(df_dict["CookingHistory"])



    """
    使い勝手(2)：料理を実際に作る。

    - 「Cooking」と「CookingHistory」に同時に登録される。
        - 既にCookingに同じ組成の料理があれば、新しくCookingには登録されない。
    -  以下、例として別の料理「ペペロンチーノ」を作成する。
        - 同じく入力は「df_food_and_grams」「df_cooking_attributes」の2つである。
        - backend_op.add_cooking_history()を呼び出す。
        - これら2つの変数は本来はStreamLitのUI操作で生成するが、今回はサンプルとして直に生成する。
    """
    print("=========「使い勝手(2)のデモ」==========")
    ### 例として「アーリオ・オーリオ・ペペロンチーノ」を登録する
    dict = []
    dict.append({"FoodDataID":9, "Grams":5})   # にんにく1かけ
    dict.append({"FoodDataID":5, "Grams":24})  # オリーブオイル大さじ2
    dict.append({"FoodDataID":10, "Grams":90}) # 乾麺パスタ1食分
    df_food_and_grams = pd.DataFrame(dict)     # （ペペロンチーノと言いつつも材料に塩と唐辛子が入っていないですが無視してください）

    dict = []
    dict.append({"CookingName":"アーリオ・オーリオ・ペペロンチーノ", "isFavorite":False, "LastUpdateDate":datetime.now(), "Description":"シンプルなものほど作るのが難しい。"})
    df_cooking_attributes = pd.DataFrame(dict)

    # 料理を作成する
    backend_op.add_cooking_history(df_food_and_grams, df_cooking_attributes)

    ### 操作後のDataBaseはこちら
    print("### 操作後のDataBaseはこちら ###")
    df_dict = backend_op.get_df_from_db()
    print("【Cookingテーブル】")
    print(df_dict["Cooking"])
    print("【CookingFoodDataテーブル】")
    print(df_dict["CookingFoodData"])
    print("【CookingHistoryテーブル】")
    print(df_dict["CookingHistory"])
    return
    
#________________________________________________________________________________________________________________________
if __name__ == "__main__":
    main()