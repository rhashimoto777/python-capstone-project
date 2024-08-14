import pandas as pd
import pytest

from src.backend_main import BackEndOperator


@pytest.fixture
def backend_operator():
    # テスト用のBackEndOperatorインスタンスを作成
    return BackEndOperator()


def test_get_df_from_db(backend_operator):
    # DBからDataFrameを取得するメソッドのテスト
    df_dict = backend_operator.get_df_from_db()
    assert isinstance(df_dict, dict)
    assert "Cooking" in df_dict
    assert "CookingFoodData" in df_dict
    assert "FoodData" in df_dict


def test_get_cooking_details(backend_operator):
    # 料理の詳細情報を取得するメソッドのテスト
    details = backend_operator.get_cooking_details()
    assert isinstance(details, list)
    assert len(details) > 0
    for detail in details:
        assert "CookingID" in detail
        assert "CookingAttribute" in detail
        assert "FoodAttribute" in detail


def test_add_cooking(backend_operator):
    # 新しい料理を追加するメソッドのテスト
    df_food_and_grams = pd.DataFrame({"FoodDataID": [1, 2], "Grams": [100, 200]})
    df_cooking_attributes = pd.DataFrame(
        {
            "CookingName": ["Test Cooking"],
            "Description": ["Test Description"],
            "IsFavorite": [False],
            "LastUpdateDate": [pd.Timestamp.now()],
        }
    )
    cooking_id = backend_operator.add_cooking(df_food_and_grams, df_cooking_attributes)
    assert cooking_id is not None


def test_add_cooking_history(backend_operator):
    # 料理履歴を追加するメソッドのテスト
    pass
    # cooking_id = 1  # 既存のCookingIDを使用
    # backend_operator.add_cooking_history(cooking_id)
    # 追加された履歴を検証するためのアサーションを追加


def test_replace_refrigerator(backend_operator):
    # 冷蔵庫の内容を置き換えるメソッドのテスト
    df_refrigerator = pd.DataFrame({"FoodDataID": [1, 2], "Grams": [100, 200]})
    backend_operator.replace_refrigerator(df_refrigerator)
    # 置き換え後の内容を検証するためのアサーションを追加
