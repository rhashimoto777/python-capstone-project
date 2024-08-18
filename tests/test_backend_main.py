import pandas as pd
import pytest

from src.backend_main import BackEndOperator
from src.datatype import my_struct as myst


@pytest.fixture
def backend_operator() -> BackEndOperator:
    """
    テスト用のBackEndOperatorインスタンスを作成する。
    """
    return BackEndOperator()


def test_raw_df(backend_operator):
    """
    BackEndOperatorのインスタンス生成時と同時に、raw_dfが正常に生成されるかを確認する。
    """
    # DBからDataFrameを取得できているかを確認する。
    raw_df = backend_operator.raw_df
    assert isinstance(raw_df, myst.RawDataFrame)

    # 得られたDataFrameに対して妥当性を確認する
    # ... 共通処理を関数内関数として定義しておく
    def check_keys_exist(df: pd.DataFrame, required_keys: list[str]):
        return all([k in df.columns for k in required_keys])

    # ... 明らかにkey名としてあり得ない文字列がkey名に含まれないことを確認する。（上記関数内関数の妥当性確認のため）
    assert not check_keys_exist(raw_df.df_fooddata, ["dsfagfsdagasdga"])

    # ... FoodDataテーブル
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

    # ... CookingFoodDataテーブル
    assert check_keys_exist(
        raw_df.df_cookingfooddata,
        [
            "CookingID",
            "FoodDataID",
        ],
    )

    # ... Cookingテーブル
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

    # ... CookingHistoryテーブル
    assert check_keys_exist(
        raw_df.df_cookinghistory,
        [
            "CookingHistoryID",
            "CookingID",
            "IssuedDate",
        ],
    )

    # ... Refrigeratorテーブル
    assert check_keys_exist(
        raw_df.df_refrigerator,
        [
            "FoodDataID",
            "Grams",
        ],
    )

    # ... ShoppingFoodDataテーブルの作成
    assert check_keys_exist(
        raw_df.df_shoppingfooddata,
        [
            "ShoppingHistoryID",
            "FoodDataID",
            "Grams",
        ],
    )

    # ... ShoppingHistoryテーブルの作成
    assert check_keys_exist(
        raw_df.df_shoppinghistory,
        [
            "ShoppingHistoryID",
            "IssuedDate",
        ],
    )


def test_cooking_info_list(backend_operator):
    """
    BackEndOperatorのインスタンス生成時と同時に、raw_dfが正常に生成されるかを確認する。
    """
    # DBからDataFrameを取得できているかを確認する。
    cilist = backend_operator.cooking_info_list
    assert isinstance(cilist, myst.CookingInfoList)

    # cilistに異常な値が入っていないことは、CookingInfoListデータクラスの__pre_init__でチェック済。
    # ここでは、何らか空ではない値が入っていることを確認する。
    # (前提として、DBに登録されているファイルには1つ以上の料理が登録されているとする)
    assert len(cilist.cookings) > 0


# def test_add_cooking(backend_operator):
#     # 新しい料理を追加するメソッドのテスト
#     df_food_and_grams = pd.DataFrame({"FoodDataID": [1, 2], "Grams": [100, 200]})
#     df_cooking_attributes = pd.DataFrame(
#         {
#             "CookingName": ["Test Cooking"],
#             "Description": ["Test Description"],
#             "IsFavorite": [False],
#             "LastUpdateDate": [pd.Timestamp.now()],
#         }
#     )
#     cooking_id = backend_operator.add_cooking(df_food_and_grams, df_cooking_attributes)
#     assert cooking_id is not None


# def test_add_cooking_history(backend_operator):
#     # 料理履歴を追加するメソッドのテスト
#     pass
#     # cooking_id = 1  # 既存のCookingIDを使用
#     # backend_operator.add_cooking_history(cooking_id)
#     # 追加された履歴を検証するためのアサーションを追加


# def test_replace_refrigerator(backend_operator):
#     # 冷蔵庫の内容を置き換えるメソッドのテスト
#     df_refrigerator = pd.DataFrame({"FoodDataID": [1, 2], "Grams": [100, 200]})
#     backend_operator.replace_refrigerator(df_refrigerator)
#     # 置き換え後の内容を検証するためのアサーションを追加
