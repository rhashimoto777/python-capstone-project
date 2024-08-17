from datetime import datetime

import pandas as pd

from src.backend_app import backend_common as common
from src.backend_app import df_analysis, sqlite_db
from src.datatype import my_struct as myst
from src.datatype.my_enum import TableName


class Singleton(object):
    def __new__(cls, *args, **kargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance


class BackEndOperator(Singleton):
    def __init__(self):
        common.system_msg_print("********** Generating Backend Instance ********")
        common.init()
        self.db_operator = sqlite_db.DataBaseOperator()
        self.raw_df = None
        self.cooking_info_list = None
        self.__pull_data()

    # ________________________________________________________________________________________________________________________
    # global関数群

    def register_new_cooking(self, cooking_info: myst.CookingInfo) -> None:
        if self.judge_same_cooking_already_exist(cooking_info) is None:
            df_c, df_cfd = df_analysis.gen_df_from_cooking_info(
                self.raw_df, cooking_info
            )
            self.__push_table_by_append(TableName.Cooking, df_c)
            self.__push_table_by_append(TableName.CookingFoodData, df_cfd)
        else:
            raise ValueError("既に同じ食材構成の料理が登録されています")
        return

    def judge_same_cooking_already_exist(self, cooking_info: myst.CookingInfo):
        return df_analysis.judge_same_cooking_already_exist(
            self.cooking_info_list, cooking_info
        )

    def add_cooking_history(self, cooking_id):
        """
        「料理を実際に作る」に相当する操作。
        CookingHistoryに料理を追加し、同時に料理に必要な材料を冷蔵庫から差し引く。
        冷蔵庫に十分な在庫が無い場合は何もせず、Falseを返す。
        """
        fg_can_cook, df_cookinghistory, df_rf_after_cooking = (
            df_analysis.gen_df_to_add_cooking_history(
                self.raw_df, self.cooking_info_list, cooking_id
            )
        )

        if fg_can_cook:
            self.__push_table_by_append(TableName.CookingHistory, df_cookinghistory)
            self.replace_refrigerator(df_rf_after_cooking)
            return True
        else:
            return False

    def replace_refrigerator(self, df_refrigerator):
        """
        Refrigeratorテーブルの中身を置き換える。 (ユーザーが直接Refrigeratorの中身を編集するような操作に対応)
        """
        self.__push_table_by_replace(TableName.Refrigerator, df_refrigerator)
        return

    # ________________________________________________________________________________________________________________________
    # private関数群
    def __pull_data(self):
        """
        SQLiteDBをDataFrameに変換し、classのメンバ変数に上書きする。
        """
        self.raw_df = self.db_operator.get_raw_df()
        self.cooking_info_list = df_analysis.gen_cooking_info_list(self.raw_df)
        return

    def __push_table_by_append(self, table_name, df):
        """
        dfの分だけ新しい行をtableに加える。
        append_dbtable_from_dfを直接呼ばずにこの関数を設けているのは、DBを更新した直後に確実にpullするようにするため。
        """
        self.db_operator.set_table_by_append(table_name, df)
        self.__pull_data()  # push直後に確実にpullを行う
        return

    def __push_table_by_replace(self, table_name: TableName, df: pd.DataFrame):
        """
        既存のtableを削除し、dfから生成される新しいtableに置き換える。
        append_dbtable_from_dfを直接呼ばずにこの関数を設けているのは、DBを更新した直後に確実にpullするようにするため。
        """
        self.db_operator.set_table_by_replace(table_name, df)
        self.__pull_data()  # push直後に確実にpullを行う
        return
