import pandas as pd

from src import util
from src.backend_app import common_info as common
from src.backend_app import data_analysis as anly
from src.backend_app import sqlite_db
from src.datatype import my_struct as myst
from src.datatype.my_enum import TableName


# ________________________________________________________________________________________________________________________
class Singleton(object):
    """
    BackEndOperator内では、各種操作ごとに毎回DataBaseにアクセスして速度が遅くなることを防ぐため、
    DataBaseと対になるメンバ変数を持っている。このメンバ変数は常にDataBaseと整合している必要がある。
    もし仮にBackEndOperatorのインスタンスが2つ以上生成されると、インスタンスAがDataBaseを更新したときに
    インスタンスB内のメンバ変数を同時に反映することが出来ず、メンバ変数とDataBaseとが整合しなくなる可能性が生じる。
    そのため、BackEndOperatorのインスタンスは常に1つである必要がある。
    (一方で初期化・値共有の実装簡便化のため、ModuledではなくClassで実装したい)

    BackEndOperatorのインスタンスは、moduleであり単一インスタンスであることが保証されているtranslator内でしか
    インスタンス生成しないため、基本的にBackEndOperatorのインスタンスは1つだけであるが、
    念のため実装上の保証としてSingletonデザインパターンを使ってインスタンスが1つだけにしかならないようにする。
    """

    def __new__(cls, *args, **kargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance


# ________________________________________________________________________________________________________________________
class BackEndOperator(Singleton):
    def __init__(self, user_id="user_default"):
        util.backend_system_msg(f"********** Generating Backend Instance (used_id = {user_id}) ********")
        common.init(user_id)
        self.db_operator = sqlite_db.DataBaseOperator()
        self.raw_df = None
        self.cooking_info_list = None
        self.__pull_data()

    # ********************* global関数群 *********************

    def register_new_cooking(self, cooking_info: myst.CookingInfo) -> None:
        existing = anly.find_same_cooking(self.cooking_info_list, cooking_info)
        if existing is None:
            df_c, df_cfd, cid = anly.gen_df_to_register_c(self.raw_df, cooking_info)
            self.push_table_by_append(TableName.Cooking, df_c)
            self.push_table_by_append(TableName.CookingFoodData, df_cfd)
        else:
            raise ValueError("既に同じ食材構成の料理が登録されています")
        return cid

    def add_cooking_history(self, cooking_id):
        """
        「料理を実際に作る」に相当する操作。
        CookingHistoryに料理を追加し、同時に料理に必要な材料を冷蔵庫から差し引く。
        冷蔵庫に十分な在庫が無い場合は何もせず、Falseを返す。
        """
        fg_can_cook, df_cookinghistory, df_rf_after_cooking = (
            anly.gen_df_to_add_cooking_history(
                self.raw_df, self.cooking_info_list, cooking_id
            )
        )

        if fg_can_cook:
            self.push_table_by_append(TableName.CookingHistory, df_cookinghistory)
            self.push_table_by_replace(TableName.Refrigerator, df_rf_after_cooking)
            return True
        else:
            return False

    def push_table_by_append(self, table_name, df):
        """
        dfの分だけ新しい行をtableに加える。
        append_dbtable_from_dfを直接呼ばずにこの関数を設けているのは、DBを更新した直後に確実にpullするようにするため。
        """
        self.db_operator.set_table_by_append(table_name, df)
        self.__pull_data()  # push直後に確実にpullを行う
        return

    def push_table_by_replace(self, table_name: TableName, df: pd.DataFrame):
        """
        既存のtableを削除し、dfから生成される新しいtableに置き換える。
        append_dbtable_from_dfを直接呼ばずにこの関数を設けているのは、DBを更新した直後に確実にpullするようにするため。
        """
        self.db_operator.set_table_by_replace(table_name, df)
        self.__pull_data()  # push直後に確実にpullを行う
        return

    # ********************* private関数群 *********************
    def __pull_data(self):
        """
        SQLiteDBをDataFrameに変換し、classのメンバ変数に上書きする。
        """
        self.raw_df = self.db_operator.get_raw_df()
        self.cooking_info_list = anly.gen_cooking_info_list(self.raw_df)
        return
