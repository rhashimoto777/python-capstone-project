from datetime import datetime
from typing import Tuple

import pandas as pd

from src import backend_main
from src.backend_app import common_info as common
from src.backend_app import data_analysis as anly
from src.backend_app import save_user_selection, user_id_manager
from src.datatype import my_struct as myst
from src.datatype.my_enum import PFC, TableName
from src.util import backend_system_msg, g_to_kcal

# classではなくmodule直下にBackEndOperatorのインスタンスを置くことで、確実にインスタンスが1つだけの状態にする。
backend_system_msg("translator.py initialization")
backend_op = backend_main.BackEndOperator()
userman = user_id_manager.UserIdManager()


def switch_user(user_id=common.USER_DEFAULT):
    backend_op.switch_user(user_id)
    userman.switch_user(common.USER_ID)
    return


def get_user_id_manager() -> Tuple[user_id_manager.UserIdManager, str]:
    return userman, common.USER_ID


def get_save_user_selection_instance() -> save_user_selection.SaveUserSelection:
    return save_user_selection.SaveUserSelection()


# _______________________________________________________________________
#                      Get系関数群：DataFrameの取得
# __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/
def get_df_all() -> myst.RawDataFrame:
    """
    全てのテーブルのDataFrameを包含する辞書を取得する。
    raw_df = get_df_all()
    df_xxx = raw_df["テーブル名"]
    のようにアクセスすれば個別テーブルのDataFrameを取得できる。
    """
    return backend_op.raw_df


def get_df_fooddata() -> pd.DataFrame:
    """個別テーブルのDataFrameを取得する。"""
    return backend_op.raw_df.df_fooddata


def get_df_cookingfooddata() -> pd.DataFrame:
    """個別テーブルのDataFrameを取得する。"""
    return backend_op.raw_df.df_cookingfooddata


def get_df_cooking() -> pd.DataFrame:
    """個別テーブルのDataFrameを取得する。"""
    return backend_op.raw_df.df_cooking


def get_df_cookinghistory() -> pd.DataFrame:
    """個別テーブルのDataFrameを取得する。"""
    return backend_op.raw_df.df_cookinghistory


def get_df_refrigerator() -> pd.DataFrame:
    """個別テーブルのDataFrameを取得する。"""
    return backend_op.raw_df.df_refrigerator


def get_df_shoppingfooddata() -> pd.DataFrame:
    """個別テーブルのDataFrameを取得する。"""
    return backend_op.raw_df.df_shoppingfooddata


def get_df_shoppinghistory() -> pd.DataFrame:
    """個別テーブルのDataFrameを取得する。"""
    return backend_op.raw_df.df_shoppinghistory


# _______________________________________________________________________
#                      Get系関数群：各種解釈情報の取得
# __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/


def get_cooking_info_list() -> myst.CookingInfoList:
    return backend_op.cooking_info_list


def judge_is_new_cooking(cooking_info: myst.CookingInfo) -> bool:
    cooking_id = anly.find_same_cooking(
        existing_cooking_list=backend_op.cooking_info_list, new_cooking=cooking_info
    )
    return cooking_id is None


# _______________________________________________________________________
#                      Set系関数群：何らかDBに値を書き込む操作
# __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/
def register_new_cooking(cooking_info: myst.CookingInfo) -> None:
    backend_op.register_new_cooking(cooking_info)
    return


def add_cooking_history(cooking_id):
    """backend_main.py内の説明を参照"""
    backend_op.add_cooking_history(cooking_id)
    return


def replace_refrigerator(df_refrigerator_new):
    """backend_main.py内の説明を参照"""
    backend_op.push_table_by_replace(TableName.Refrigerator, df_refrigerator_new)
    return


# _______________________________________________________________________
#                      お役立ち系
# __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/
def gen_food_info(food_id: int, grams: float) -> myst.FoodInfoOfCooking:
    try:
        df_f = backend_op.raw_df.df_fooddata
        if food_id not in df_f["FoodDataID"].tolist():
            raise ValueError(f"存在しないFoodDataID({food_id})です")

        df_f_row = df_f[df_f["FoodDataID"] == food_id]
        del df_f
        food_name = df_f_row["FoodName"].values[0]
        standard_unit_name = df_f_row["StandardUnit_Name"].values[0]
        standard_unit_grams = df_f_row["StandardUnit_Grams"].values[0]
        standard_unit_numbers = grams / standard_unit_grams
        grams_protein = standard_unit_numbers * df_f_row["Grams_Protein"].values[0]
        grams_fat = standard_unit_numbers * df_f_row["Grams_Fat"].values[0]
        grams_carbo = standard_unit_numbers * df_f_row["Grams_Carbo"].values[0]
        calory_total = standard_unit_numbers * df_f_row["Calory_Total"].values[0]
        caloty_protein = g_to_kcal(grams_protein, PFC.Protein)
        caloty_fat = g_to_kcal(grams_fat, PFC.Fat)
        caloty_carbo = g_to_kcal(grams_carbo, PFC.Carbo)

        food_info = myst.FoodInfoOfCooking(
            fooddata_id=food_id,
            food_name=food_name,
            standard_unit_name=standard_unit_name,
            standard_unit_grams=standard_unit_grams,
            standard_unit_numbers=standard_unit_numbers,
            calory_total=calory_total,
            caloty_protein=caloty_protein,
            caloty_fat=caloty_fat,
            caloty_carbo=caloty_carbo,
            grams_total=grams,
            grams_protein=grams_protein,
            grams_fat=grams_fat,
            grams_carbo=grams_carbo,
            is_present_in_refrigerator=True,
        )
    except Exception as e:
        raise ValueError(f"FoodInfoOfCookingインスタンスへの変換に失敗 : {e}")
    return food_info


def gen_cooking_info(
    cooking_name: str,
    is_favorite: bool,
    last_update_date: datetime,
    description: str,
    food_attr: list[myst.FoodInfoOfCooking],
) -> myst.CookingInfo:
    try:
        calory_total = sum([f.calory_total for f in food_attr])
        caloty_protein = sum([f.caloty_protein for f in food_attr])
        caloty_fat = sum([f.caloty_fat for f in food_attr])
        caloty_carbo = sum([f.caloty_carbo for f in food_attr])

        grams_protein = sum([f.grams_protein for f in food_attr])
        grams_fat = sum([f.grams_fat for f in food_attr])
        grams_carbo = sum([f.grams_carbo for f in food_attr])

        is_present_in_refrigerator = all(
            [f.is_present_in_refrigerator for f in food_attr]
        )
        cooking_id = 0  # 仮値

        cooking_info = myst.CookingInfo(
            # ****** Cookingテーブルに元々存在する情報 ******
            cooking_id=cooking_id,
            cooking_name=cooking_name,
            is_favorite=is_favorite,
            last_update_date=last_update_date,
            description=description,
            # ****** 他テーブルと合わせて解釈した情報 ******
            # カロリー[kcal]の情報
            calory_total=calory_total,
            caloty_protein=caloty_protein,
            caloty_fat=caloty_fat,
            caloty_carbo=caloty_carbo,
            # P/F/Cのグラム数
            grams_protein=grams_protein,
            grams_fat=grams_fat,
            grams_carbo=grams_carbo,
            # 食材ごとの栄養情報
            food_attribute=food_attr,
            # 全ての食材が冷蔵庫に必要なグラム数が存在するか
            is_present_in_refrigerator=is_present_in_refrigerator,
        )
    except Exception as e:
        raise ValueError(f"CookingInfoインスタンスへの変換に失敗 : {e}")
    return cooking_info
