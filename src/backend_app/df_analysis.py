from dataclasses import replace
from datetime import datetime
from typing import Optional, Tuple

import pandas as pd

from src.datatype import my_struct as myst
from src.datatype.my_enum import PFC
from src.util import g_to_kcal


def gen_cooking_info_list(raw_df: myst.RawDataFrame) -> myst.CookingInfoList:
    """
    Gookingごとの総カロリー・総P/F/C量などの情報を返す。
    """
    # DB由来のDataFrameを取得
    df_c = raw_df.df_cooking

    cookings = []
    for i in range(len(df_c)):
        df_c_row = df_c.iloc[i]
        # Cookingテーブルに元々存在する情報
        cooking_id = df_c_row["CookingID"]
        cooking_name = df_c_row["CookingName"]
        is_favorite = df_c_row["IsFavorite"]
        last_update_date = df_c_row["LastUpdateDate"]
        description = df_c_row["Description"]

        # 他テーブルと合わせて解釈した情報
        food_attr = __gen_food_info_list_of_cooking(raw_df, cooking_id)
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

        # CookingInfoを生成する
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
        cookings.append(cooking_info)

    ret = myst.CookingInfoList(cookings=cookings)
    return ret


def __gen_food_info_list_of_cooking(
    raw_df: myst.RawDataFrame, cooking_id: int
) -> list[myst.FoodInfoOfCooking]:
    df_cf = raw_df.df_cookingfooddata
    df_f = raw_df.df_fooddata

    ########### (1) あるCookingIDを持つCookingを構成する、食材ごとのカロリー情報を生成する ###########
    df_merge = df_cf[df_cf["CookingID"] == cooking_id].merge(df_f, on="FoodDataID")

    ret = []
    for i in range(len(df_merge)):
        df_merge_row = df_merge.iloc[i]

        # Fooddataテーブルに元々存在する情報
        fooddata_id = df_merge_row["FoodDataID"]
        food_name = df_merge_row["FoodName"]
        standard_unit_name = df_merge_row["StandardUnit_Name"]
        standard_unit_grams = df_merge_row["StandardUnit_Grams"]

        # CookingFooddataテーブルに元々存在する情報
        grams_total = df_merge_row["Grams"]

        # 新たに解釈した情報
        standard_unit_numbers = grams_total / standard_unit_grams

        grams_protein = standard_unit_numbers * df_merge_row["Grams_Protein"]
        grams_fat = standard_unit_numbers * df_merge_row["Grams_Fat"]
        grams_carbo = standard_unit_numbers * df_merge_row["Grams_Carbo"]

        calory_total = standard_unit_numbers * df_merge_row["Calory_Total"]
        caloty_protein = g_to_kcal(grams_protein, PFC.Protein)
        caloty_fat = g_to_kcal(grams_fat, PFC.Fat)
        caloty_carbo = g_to_kcal(grams_carbo, PFC.Carbo)

        # is_present_in_refrigeratorに仮で値を入れて生成する。
        food_info = myst.FoodInfoOfCooking(
            fooddata_id=fooddata_id,
            food_name=food_name,
            standard_unit_name=standard_unit_name,
            standard_unit_grams=standard_unit_grams,
            standard_unit_numbers=standard_unit_numbers,
            calory_total=calory_total,
            caloty_protein=caloty_protein,
            caloty_fat=caloty_fat,
            caloty_carbo=caloty_carbo,
            grams_total=grams_total,
            grams_protein=grams_protein,
            grams_fat=grams_fat,
            grams_carbo=grams_carbo,
            is_present_in_refrigerator=True,
        )
        judge = __judge_food_exist_in_refragerator(raw_df, food_info)
        food_info = replace(food_info, is_present_in_refrigerator=judge)
        ret.append(food_info)
    return ret


def __judge_food_exist_in_refragerator(
    raw_df: myst.RawDataFrame, food_info: myst.FoodInfoOfCooking
) -> bool:
    food_id = food_info.fooddata_id
    c_food_gram = food_info.grams_total

    df_rfrg = raw_df.df_refrigerator
    if food_id not in df_rfrg["FoodDataID"].to_list():
        return False
    df_rfrg_fid = df_rfrg[df_rfrg["FoodDataID"] == food_id]
    r_food_gram = df_rfrg_fid["Grams"].values[0]
    if r_food_gram >= c_food_gram:
        return True
    else:
        return False


def gen_df_to_register_c(
    raw_df: myst.RawDataFrame, cooking_info: myst.CookingInfo
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df_c = raw_df.df_cooking
    cooking_id = __issue_new_id(df_c["CookingID"].tolist())

    dict_cookingfooddata = []
    for fd in cooking_info.food_attribute:
        dict_cookingfooddata.append(
            {
                "CookingID": cooking_id,
                "FoodDataID": fd.fooddata_id,
                "Grams": fd.grams_total,
            }
        )

    dict_cooking = []
    dict_cooking.append(
        {
            "CookingID": cooking_id,
            "CookingName": cooking_info.cooking_name,
            "isFavorite": cooking_info.is_favorite,
            "LastUpdateDate": cooking_info.last_update_date,
            "Description": cooking_info.description,
        }
    )

    return pd.DataFrame(dict_cooking), pd.DataFrame(dict_cookingfooddata), cooking_id


def __issue_new_id(existing_id_list: list[int]) -> int:
    """
    既存のIDのリストを入力に取り、既存のIDとは被らない新しいIDを発行する。
    このとき、なるべく小さい値を新しいIDとして発行する。
    """
    if len(existing_id_list) == 0:
        return 0
    id_max = max(existing_id_list)
    for i in range(id_max):
        if i in existing_id_list:
            continue
        else:
            return i
    return id_max + 1


def find_same_cooking(
    existing_cooking_list: myst.CookingInfoList,
    new_cooking: myst.CookingInfo,
) -> Optional[int]:
    def gen_df_from_foodlist(flist: list[myst.FoodInfoOfCooking]) -> pd.DataFrame:
        dict = [{"ID": f.fooddata_id, "Grams": f.grams_total} for f in flist]
        return pd.DataFrame(dict)

    def judge_df_are_equal(df1: pd.DataFrame, df2: pd.DataFrame) -> bool:
        df1_sorted = (
            df1.sort_index(axis=1)
            .sort_values(by=df1.columns.tolist())
            .reset_index(drop=True)
        )
        df2_sorted = (
            df2.sort_index(axis=1)
            .sort_values(by=df2.columns.tolist())
            .reset_index(drop=True)
        )
        are_equal = df1_sorted.equals(df2_sorted)
        return are_equal

    df1 = gen_df_from_foodlist(new_cooking.food_attribute)
    for eck in existing_cooking_list.cookings:
        df2 = gen_df_from_foodlist(eck.food_attribute)
        if judge_df_are_equal(df1, df2):
            return eck.cooking_id
    return None


def gen_df_to_add_cooking_history(
    raw_df: myst.RawDataFrame, cooking_list: myst.CookingInfoList, cooking_id: int
) -> Tuple[bool, Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    cooking_info = convert_cooking_id_to_cooking_info(cooking_list, cooking_id)
    if cooking_info is None:
        raise ValueError(f"存在しないcooking_id{cooking_id}が入力されました")

    # 冷蔵庫内に必要な材料が十分なグラム数あるかを確認する。
    fg_can_cook, df_rf_after_cooking = check_possible_to_make_cooking(cooking_info)

    if fg_can_cook:
        h_id = __issue_new_id(raw_df.df_cookinghistory["CookingHistoryID"].tolist())

        dict_cookinghistory = []
        dict_cookinghistory.append(
            {
                "CookingHistoryID": h_id,
                "CookingID": cooking_id,
                "IssuedDate": datetime.now(),
            }
        )
        return fg_can_cook, pd.DataFrame(dict_cookinghistory), df_rf_after_cooking
    else:
        return fg_can_cook, None, None


def convert_cooking_id_to_cooking_info(
    cooking_list: myst.CookingInfoList, cooking_id: int
) -> Optional[myst.CookingInfo]:
    cooking_info = None
    for ck in cooking_list.cookings:
        if cooking_id == ck.cooking_id:
            cooking_info = ck
            break
    return cooking_info


def check_possible_to_make_cooking(
    raw_df: myst.RawDataFrame, cookinf_info: myst.CookingInfo
):
    """
    IDで指定された料理を1食作るのに必要な材料が冷蔵庫にあるかどうかを確認する。
    返り値は2つである。
        第1返り値 : 料理を作ることが可能かどうかを表すboolean
        第2返り値 : 料理を作ることが可能なとき、料理の材料分を引いた冷蔵庫のDataFrameを返す。
                    (料理を作ることができないときはNoneを返す)
    """
    df_rfrg = raw_df.df_refrigerator
    df_rfrg_after_cooking = df_rfrg

    is_possible_to_make_cooking = True
    for food in cookinf_info.food_attribute:
        # 料理に使う食材のIDと必要なグラム数を取得する
        food_id = food.fooddata_id
        c_food_gram = food.grams_total

        # 対応する食材の冷蔵庫内のグラム数を取得する

        if food_id not in df_rfrg["FoodDataID"].to_list():
            is_possible_to_make_cooking = False
            break

        df_rfrg_fid = df_rfrg[df_rfrg["FoodDataID"] == food_id]
        r_food_gram = df_rfrg_fid["Grams"].values[0]

        # 冷蔵庫内のグラム数が料理に必要なグラム数より多いかどうかを判定する
        if r_food_gram >= c_food_gram:
            df_rfrg_after_cooking.loc[df_rfrg_fid.index, "Grams"] -= c_food_gram
        else:
            is_possible_to_make_cooking = False
            break

    if not is_possible_to_make_cooking:
        df_rfrg_after_cooking = None

    return is_possible_to_make_cooking, df_rfrg_after_cooking
