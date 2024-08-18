import pandas as pd
import pytest

from src.backend_app import df_analysis as anly
from src.backend_main import BackEndOperator
from src.datatype import my_struct as myst
from tests import test_my_struct
from src.datatype.my_enum import TableName


@pytest.fixture(autouse=True)
def setup_and_teardown():
    """
    テストの実行前後でDataBase値が変わらないようにする。
    """

    # テスト用のBackEndOperatorインスタンスを作成する
    beo = BackEndOperator()

    # DataFrameのバックアップ
    orig = beo.raw_df

    # テスト実行
    yield beo

    # テスト後に元の値に戻す
    beo.push_table_by_replace(TableName.FoodData, orig.df_fooddata)
    beo.push_table_by_replace(TableName.CookingFoodData, orig.df_cookingfooddata)
    beo.push_table_by_replace(TableName.Cooking, orig.df_cooking)
    beo.push_table_by_replace(TableName.CookingHistory, orig.df_cookinghistory)
    beo.push_table_by_replace(TableName.Refrigerator, orig.df_refrigerator)
    beo.push_table_by_replace(TableName.ShoppingFoodData, orig.df_shoppingfooddata)
    beo.push_table_by_replace(TableName.ShoppingHistory, orig.df_shoppinghistory)

    # 念のため、本当に復元された確認
    restored = beo.raw_df
    assert orig.df_fooddata.equals(restored.df_fooddata)
    assert orig.df_cookingfooddata.equals(restored.df_cookingfooddata)
    assert orig.df_cooking.equals(restored.df_cooking)
    assert orig.df_cookinghistory.equals(restored.df_cookinghistory)
    assert orig.df_refrigerator.equals(restored.df_refrigerator)
    assert orig.df_shoppingfooddata.equals(restored.df_shoppingfooddata)
    assert orig.df_shoppinghistory.equals(restored.df_shoppinghistory)
    return


def test_raw_df(setup_and_teardown):
    """
    BackEndOperatorのインスタンス生成時と同時に、raw_dfが正常に生成されるかを確認する。
    (__init__メソッド、__pull_dataメソッドのテストも兼ねる)
    """
    backend_operator = setup_and_teardown

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


def test_cooking_info_list(setup_and_teardown):
    """
    BackEndOperatorのインスタンス生成時と同時に、raw_dfが正常に生成されるかを確認する。
    (__init__メソッド、__pull_dataメソッドのテストも兼ねる)
    """
    backend_operator = setup_and_teardown

    # DBからDataFrameを取得できているかを確認する。
    cilist = backend_operator.cooking_info_list
    assert isinstance(cilist, myst.CookingInfoList)

    # cilistに異常な値が入っていないことは、CookingInfoListデータクラスの__pre_init__でチェック済。
    # ここでは、何らか空ではない値が入っていることを確認する。
    # (前提として、DBに登録されているファイルには1つ以上の料理が登録されているとする)
    assert len(cilist.cookings) > 0
    return


def test_register_cooking(setup_and_teardown):
    """
    registor_cooking関数のテスト
    """
    backend_operator = setup_and_teardown
    df_c_orig = backend_operator.raw_df.df_cooking

    # 有効かつ空ではないなCookingInfoインスタンスを生成する。
    # 加えて関数実行前のcooking_idのリストを取得しておく
    cooking_info: myst.CookingInfo = test_my_struct.gen_valid_cooking_info_instance()
    existing_id_list = df_c_orig["CookingID"].tolist()

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


def test_add_cooking_history_01(setup_and_teardown):
    """
    add_cooking_history関数のテスト。
    この関数では「料理が作れた」時の挙動を扱う。
    """
    backend_operator = setup_and_teardown
    df_ch_orig = backend_operator.raw_df.df_cookinghistory
    df_r_orig = backend_operator.raw_df.df_refrigerator
    df_c_orig = backend_operator.raw_df.df_cooking

    # 既存のCookingHistoryに確実に存在しないCookingIDを用意するため、新しい料理を登録する。
    # 新しい料理が登録できなかった場合はテストが実行できないため、テスト条件の不良としてassertで落とす。
    cooking_info: myst.CookingInfo = test_my_struct.gen_valid_cooking_info_instance()
    cooking_id = backend_operator.register_new_cooking(cooking_info)
    assert cooking_id is not None
    assert cooking_id not in df_c_orig["CookingID"].tolist()
    assert cooking_id not in df_ch_orig["CookingID"].tolist()
    del df_c_orig

    # 関数を実行する。実際に料理が作れなかった場合は後のテストが無意味になるため、assertで落とす。
    try:
        ret = backend_operator.add_cooking_history(cooking_id)
    except Exception as e:
        pytest.fail(f"pytest failed : {e}")
    assert ret

    # CookingHistoryテーブルに値が追加されているかチェックする
    df_ch_after = backend_operator.raw_df.df_cookinghistory
    assert not df_ch_orig.equals(df_ch_after)
    assert len(df_ch_orig) + 1 == len(df_ch_after)
    assert df_ch_after.iloc[-1].loc["CookingID"] == cooking_id

    # Refrigeratorテーブルから値が引かれているかを確認する
    def get_grams(df_r, food_id):
        return df_r[df_r["FoodDataID"] == food_id]["Grams"].values[0]

    df_r_after = backend_operator.raw_df.df_refrigerator
    cooking_info = None
    for c in backend_operator.cooking_info_list.cookings:
        if c.cooking_id == cooking_id:
            cooking_info = c
            break
    assert cooking_info is not None
    assert len(cooking_info.food_attribute) > 0
    for food_info in cooking_info.food_attribute:
        food_id = food_info.fooddata_id
        g_orig = get_grams(df_r_orig, food_id)
        g_after = get_grams(df_r_after, food_id)

        food_grams = food_info.grams_total
        assert food_grams > 0
        assert g_orig - food_grams == g_after
    return


def test_push_table_by_replace(setup_and_teardown):
    """
    push_table_by_replace関数のテスト。
    Refrigeratorテーブルを用いる。
    """
    backend_operator = setup_and_teardown
    
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
    return
