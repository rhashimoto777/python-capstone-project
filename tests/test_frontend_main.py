import pytest
import pandas as pd
from frontend_main import FrontEndOperator

@pytest.fixture
def initial_df_dict():
    # テスト用の初期データフレーム辞書を作成
    return {
        "Table1": pd.DataFrame({"Column1": [1, 2], "Column2": [3, 4]}),
        "Table2": pd.DataFrame({"ColumnA": ["A", "B"], "ColumnB": ["C", "D"]})
    }

@pytest.fixture
def frontend_operator(initial_df_dict):
    # テスト用のFrontEndOperatorインスタンスを作成
    return FrontEndOperator(initial_df_dict)

def test_update_df_dict(frontend_operator):
    # update_df_dictメソッドのテスト
    new_df_dict = {
        "Table3": pd.DataFrame({"ColumnX": [5, 6], "ColumnY": [7, 8]})
    }
    frontend_operator.update_df_dict(new_df_dict)
    assert frontend_operator.df_dict == new_df_dict

def test_sample_show_all_df(frontend_operator, monkeypatch):
    # sample_show_all_dfメソッドのテスト
    # Streamlitのst.dataframeをモックする
    def mock_data_frame(df):
        assert not df.empty

    monkeypatch.setattr("streamlit.dataframe", mock_data_frame)
    frontend_operator.sample_show_all_df()