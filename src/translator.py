from src import backend_main
from src.datatype import my_struct

import pandas as pd

# モジュール内のトップレベルのコードは、モジュールの初回import時にしか行われない。
# translator.pyは様々な.pyファイルからimportされるが、BackEndOperator()のインスタンス生成はシステム全体を通して1回しか実行されない。
backend_op = backend_main.BackEndOperator()


def init():
    global backend_op
    backend_op = backend_main.BackEndOperator()


# _______________________________________________________________________
#                      Get系関数群：DataFrameの取得
# __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/
def get_df_all() -> my_struct.RawDataFrame:
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
def get_cooking_details() :
    """backend_main.py内の説明を参照"""
    return backend_op.get_cooking_details()

def get_cooking_info_list() -> my_struct.CookingInfoList:
    return backend_op.cooking_info_list


def check_possible_to_make_cooking(cooking_id):
    """backend_main.py内の説明を参照"""
    backend_op.check_possible_to_make_cooking(cooking_id)


# _______________________________________________________________________
#                      Set系関数群：何らかDBに値を書き込む操作
# __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/
def add_cooking(df_food_and_grams, df_cooking_attributes):
    """backend_main.py内の説明を参照"""
    is_success, msg = backend_op.add_cooking(df_food_and_grams, df_cooking_attributes)
    return is_success, msg


def add_cooking_history(cooking_id):
    """backend_main.py内の説明を参照"""
    backend_op.add_cooking_history(cooking_id)
    return


def replace_refrigerator(df_refrigerator_new):
    """backend_main.py内の説明を参照"""
    backend_op.replace_refrigerator(df_refrigerator_new)
    return
