import pandas as pd
import pytest

from src.backend_app import df_analysis as anly
from src.backend_main import BackEndOperator
from src.datatype import my_struct as myst
from tests import test_my_struct
from src.datatype.my_enum import TableName


@pytest.fixture
def backend_operator() -> BackEndOperator:
    """
    テスト用のBackEndOperatorインスタンスを作成する。
    """
    return BackEndOperator()


def test_raw_df(backend_operator):
    """
    BackEndOperatorのインスタンス生成時と同時に、raw_dfが正常に生成されるかを確認する。
    (__init__メソッド、__pull_dataメソッドのテストも兼ねる)
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
    return


def test_cooking_info_list(backend_operator):
    """
    BackEndOperatorのインスタンス生成時と同時に、raw_dfが正常に生成されるかを確認する。
    (__init__メソッド、__pull_dataメソッドのテストも兼ねる)
    """
    # DBからDataFrameを取得できているかを確認する。
    cilist = backend_operator.cooking_info_list
    assert isinstance(cilist, myst.CookingInfoList)

    # cilistに異常な値が入っていないことは、CookingInfoListデータクラスの__pre_init__でチェック済。
    # ここでは、何らか空ではない値が入っていることを確認する。
    # (前提として、DBに登録されているファイルには1つ以上の料理が登録されているとする)
    assert len(cilist.cookings) > 0
    return


def test_register_cooking(backend_operator):
    """
    registor_cooking関数のテスト
    """
    # 有効かつ空ではないなCookingInfoインスタンスを生成する。
    # 加えて関数実行前のcooking_idのリストを取得しておく
    cooking_info: myst.CookingInfo = test_my_struct.gen_valid_cooking_info_instance()
    existing_id_list = backend_operator.raw_df.df_cooking["CookingID"].tolist()

    # テストに用いたCookingInfoは、既存の料理と被っているのかを判別する。
    # もしテストに用いたCookinfInfoが既存の料理と被っている場合、後のテストで正常に試験が行えないためFailにする。
    existing_id = None
    try:
        existing_id = anly.find_same_cooking(
            backend_operator.cooking_info_list, cooking_info
        )
    except Exception as e:
        pytest.fail(f"pytest failed : {e}")

    assert existing_id is None

    # 対象関数を実行する。
    # 同時に、正常に処理実行できるかを判定する。
    try:
        cooking_id = backend_operator.register_new_cooking(cooking_info)
    except Exception as e:
        pytest.fail(f"pytest failed : {e}")

    # 新しいcooking_idが生成されたことを確認する。
    assert cooking_id is not None
    assert cooking_id not in existing_id_list
    return


def test_add_cooking_history(backend_operator):
    """
    add_cooking_history関数のテスト
    """
    # 引数として用いるCookingIDを用意する。
    # 登録済みの料理がゼロの場合はテストが実行できないため、assertで落とす。
    cooking_id_list = backend_operator.raw_df.df_cooking["CookingID"].to_list()
    assert len(cooking_id_list) > 0
    cooking_id = cooking_id_list[0]

    # 元のDataFrameの値を記憶しておく。
    df_ch_orig = backend_operator.raw_df.df_cookinghistory
    df_r_orig = backend_operator.raw_df.df_refrigerator

    # 関数を実行する
    try:
        backend_operator.add_cooking_history(cooking_id)
    except Exception as e:
        pytest.fail(f"pytest failed : {e}")

    # DataFrameを元の値に戻す
    backend_operator.push_table_by_replace(TableName.CookingHistory, df_ch_orig)
    backend_operator.push_table_by_replace(TableName.Refrigerator, df_r_orig)
    return


def test_push_table_by_replace(backend_operator):
    """
    push_table_by_replace関数のテスト。
    Refrigeratorテーブルを用いる。
    """

    def get_latest_df_refrigerator():
        return backend_operator.raw_df.df_refrigerator

    def replace_refrigerator(df):
        backend_operator.push_table_by_replace(TableName.Refrigerator, df)
        return

    # 値の準備
    df_r_orig = get_latest_df_refrigerator()
    df_r_tmp = pd.DataFrame({"FoodDataID": [1, 2], "Grams": [100, 200]})
    assert not df_r_orig.equals(df_r_tmp)

    # 関数の実行
    try:
        replace_refrigerator(df_r_tmp)
    except Exception as e:
        pytest.fail(f"pytest failed : {e}")

    # 値が書き換わったかチェック
    df_r_result = get_latest_df_refrigerator()
    assert df_r_result.equals(df_r_tmp)

    # 元々の値に戻す
    del df_r_result, df_r_tmp  # ポカ避け
    replace_refrigerator(df_r_orig)

    # 本当に戻っているのかチェック
    df_r_restored = get_latest_df_refrigerator()
    assert df_r_restored.equals(df_r_orig)
    return
