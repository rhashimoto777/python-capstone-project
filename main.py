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
    temp_add_refrigerator_food(backend_op)

    # DataBaseの各テーブルのDataframeに対応する辞書を取得する
    df_dict = backend_op.get_df_from_db()

    
    show_refrigerator_fooddata(backend_op)

    cooking_details = backend_op.get_cooking_details()

    
    frontend_op = frontend_main.FrontEndOperator(df_dict)

    # <<< 説明用デモ1 >>> : backendへの基本的な操作
    # python main.pyで実行ください。
    # sample_demo(backend_op, frontend_op)

    # <<< 説明用デモ2 >>> :（とりあえずDataBaseの内容全てをブラウザに表示）
    # 次の行をコメントアウトして、streamlit run main.py で実行できます。
    # frontend_op.sample_show_all_df() 

    # <<< 説明用デモ3 >>> : Cookingの詳細情報の取得
    # sample_get_cooking_details(cooking_details)


#________________________________________________________________________________________________________________________
def show_refrigerator_fooddata(backend_op):
    
    df_dict = backend_op.get_df_from_db()
    df_refrigerator = df_dict["Refrigerator"]
    df_fooddata = df_dict["FoodData"]
    
    frontend_op = frontend_main.FrontEndOperatorRefrigeratorFooddata(df_refrigerator, df_fooddata)
    frontend_op.show_refrigerator_fooddata_df(df_refrigerator, df_fooddata) 
    return


def temp_add_refrigerator_food(backend_op):
    """
    暫定実装、当面のテスト動作用：
    とりあえず冷蔵庫の中身に全ての食材を100単位ずつ追加する
    """
    df_dict = backend_op.get_df_from_db()
    df_fooddata = df_dict["FoodData"]
    
    dict_refrigerator = []
    for i in range(len(df_fooddata)):
        food = df_fooddata.iloc[i]
        id = food.loc["FoodDataID"]
        grams_to_add = 100 * food.loc["StandardUnit_Grams"]
        dict_refrigerator.append({"FoodDataID":id, "Grams":grams_to_add})
    df_refrigerator = pd.DataFrame(dict_refrigerator)
    backend_op.replace_refrigerator(df_refrigerator)
    return
 

def sample_get_cooking_details(cooking_details):
    """
    JIRAチケット「PCPG-13」に対応する、
    『CookingIDごとの「料理の総カロリー」、「PFCそれぞれのグラム量」、「PFCそれぞれのカロリー量」』
    に相当する情報の取得方法とデータ利用方法についてのデモ。
    """
    # cooking_details = backend_op.get_cooking_details() でデータ取得する。
    # 「cooking_details」の型の詳細は、backend_op.get_cooking_details()を直接見るのが詳細だが、本関数で簡単にデモとして内容を表示する。

    for cooking_details_elem in cooking_details:
        # cooking_detailsは、辞書型のリストになっている。1つ1つの辞書要素が個別のCookingIDに対応する。

        # CookingIDの取得
        cooking_id = cooking_details_elem["CookingID"] 
        print(f'\n=========== CookingID : {cooking_id} ===========')

        # CookingAttributeは、料理の総カロリー、総P/F/C含有量、総P/F/Cカロリー等を含む。
        # この情報を用いれば、総カロリーに占める Protein / Fat / Carbo 比、いわゆるPFCバランスを計算できる。
        cooking_attribute = cooking_details_elem["CookingAttribute"]
        print(" <<<< CookingAttribute >>>>")
        print(cooking_attribute)

        # FoodAttributeは、料理を構成する食材ごとのカロリー・P/F/C含有量、P/F/Cカロリーを含む。
        # この情報を用いれば、例えば「料理全体の脂質カロリーは何の食材によるところが大きいか」などが分析できる。
        food_attribute = cooking_details_elem["FoodAttribute"]
        print(" <<<< FoodAttribute >>>>")
        print(food_attribute)


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
        - add_cookingを読んだ後に別の関数「add_cooking_history」を呼ぶ。（2回関数を呼ぶ）
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
    cooking_id = backend_op.add_cooking(df_food_and_grams, df_cooking_attributes)
    backend_op.add_cooking_history(cooking_id)

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