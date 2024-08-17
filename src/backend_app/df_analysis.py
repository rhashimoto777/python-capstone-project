from dataclasses import replace

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
        cookings.append(cooking_id)

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
        judge = __judge_food_present_in_refragerator(raw_df, food_info)
        food_info = replace(food_info, is_present_in_refrigerator=judge)
        ret.append(food_info)
    return


def __judge_food_present_in_refragerator(
    raw_df: myst.RawDataFrame, food_info: myst.FoodInfoOfCooking
) -> bool:
    return True
