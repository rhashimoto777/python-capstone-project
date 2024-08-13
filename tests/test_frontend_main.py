import pytest
import pandas as pd
from src import frontend_main as fm

@pytest.fixture
def initial_df_dict():
    # テスト用の初期データフレーム辞書を作成
    return {
        "Table1": pd.DataFrame({"Column1": [1, 2], "Column2": [3, 4]}),
        "Table2": pd.DataFrame({"ColumnA": ["A", "B"], "ColumnB": ["C", "D"]})
    }

# @pytest.fixture
# def test_update_df_dict():
#     # update_df_dictメソッドのテスト
#     new_df_dict = {
#         "Table3": pd.DataFrame({"ColumnX": [5, 6], "ColumnY": [7, 8]})
#     }
#     fm.update_df_dict(new_df_dict)
#     assert fm.df_dict == new_df_dict
