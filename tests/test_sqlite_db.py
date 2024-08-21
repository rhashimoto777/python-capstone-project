import pandas as pd
import pytest

from src.backend_app import sqlite_db
from src.datatype.my_struct import RawDataFrame


def test_get_raw_df():
    """
    get_raw_df関数の単体テスト
    """
    # *********** DataBaseOperatorのインスタンス生成 ***********
    try:
        op = sqlite_db.DataBaseOperator()
    except Exception as e:
        pytest.fail(f"DataBaseOperatorのインスタンス生成に失敗しました : {e}")

    # *********** 対象関数の実行 ***********
    try:
        raw_df = op.get_raw_df()
    except Exception as e:
        pytest.fail(f"get_raw_df()の実行に失敗しました : {e}")

    # *********** 得られたDataFrameに対して妥当性を確認する ***********
    # 共通処理を関数内関数として定義しておく
    def check_keys_exist(df: pd.DataFrame, required_keys: list[str]):
        return all([k in df.columns for k in required_keys])

    # 明らかにkey名としてあり得ない文字列がkey名に含まれないことを確認する。（上記関数内関数の妥当性確認のため）
    assert not check_keys_exist(raw_df.df_fooddata, ["dsfagfsdagasdga"])

    # FoodDataテーブル
    assert check_keys_exist(
        raw_df.df_fooddata,
        [
            "FoodDataID",
            "FoodName",
            "Calory_Total",
            "Grams_Protein",
            "Grams_Fat",
            "Grams_Carbo",
            "StandardUnit_Name",
            "StandardUnit_Grams",
        ],
    )

    # CookingFoodDataテーブル
    assert check_keys_exist(
        raw_df.df_cookingfooddata,
        [
            "CookingID",
            "FoodDataID",
        ],
    )

    # Cookingテーブル
    assert check_keys_exist(
        raw_df.df_cooking,
        [
            "CookingID",
            "CookingName",
            "IsFavorite",
            "LastUpdateDate",
            "Description",
        ],
    )

    # CookingHistoryテーブル
    assert check_keys_exist(
        raw_df.df_cookinghistory,
        [
            "CookingHistoryID",
            "CookingID",
            "IssuedDate",
        ],
    )

    # Refrigeratorテーブル
    assert check_keys_exist(
        raw_df.df_refrigerator,
        [
            "FoodDataID",
            "Grams",
        ],
    )

    # ShoppingFoodDataテーブルの作成
    assert check_keys_exist(
        raw_df.df_shoppingfooddata,
        [
            "ShoppingHistoryID",
            "FoodDataID",
            "Grams",
        ],
    )

    # ShoppingHistoryテーブルの作成
    assert check_keys_exist(
        raw_df.df_shoppinghistory,
        [
            "ShoppingHistoryID",
            "IssuedDate",
        ],
    )

    return
