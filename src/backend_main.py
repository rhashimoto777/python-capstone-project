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

    def check_possible_to_make_cooking(self, cooking_id):
        """
        IDで指定された料理を1食作るのに必要な材料が冷蔵庫にあるかどうかを確認する。
        返り値は2つである。
          第1返り値 : 料理を作ることが可能かどうかを表すboolean
          第2返り値 : 料理を作ることが可能なとき、料理の材料分を引いた冷蔵庫のDataFrameを返す。
                      (料理を作ることができないときはNoneを返す)
        """
        df_cf = self.raw_df.df_cookingfooddata
        df_cf = df_cf[df_cf["CookingID"] == cooking_id]
        df_rfrg = self.raw_df.df_refrigerator
        df_rfrg_after_cooking = df_rfrg

        is_possible_to_make_cooking = True
        for i in range(len(df_cf)):
            # 料理に使う食材のIDと必要なグラム数を取得する
            food_id = df_cf.iloc[i].loc["FoodDataID"]
            c_food_gram = df_cf.iloc[i].loc["Grams"]

            # 対応する食材の冷蔵庫内のグラム数を取得する
            df_rfrg_fid = df_rfrg[df_rfrg["FoodDataID"] == food_id]
            r_food_gram = df_rfrg_fid["Grams"].values[0]

            # 冷蔵庫内のグラム数が料理に必要なグラム数より多意かどうかを判定する
            if r_food_gram >= c_food_gram:
                df_rfrg_after_cooking.loc[df_rfrg_fid.index, "Grams"] -= c_food_gram
            else:
                is_possible_to_make_cooking = False
                df_rfrg_after_cooking = None
                break

        return is_possible_to_make_cooking, df_rfrg_after_cooking

    def add_cooking_history(self, cooking_id):
        """
        「料理を実際に作る」に相当する操作。
        CookingHistoryに料理を追加し、同時に料理に必要な材料を冷蔵庫から差し引く。
        冷蔵庫に十分な在庫が無い場合は何もせず、Falseを返す。
        """
        # 冷蔵庫内に必要な材料が十分なグラム数あるかを確認する。
        fg_can_cook, df_rf_after_cooking = self.check_possible_to_make_cooking(
            cooking_id
        )

        if fg_can_cook:
            # CookingHistoryに料理を追加する
            new_cooking_history_id = self.__issue_new_id(
                self.raw_df.df_cookinghistory["CookingHistoryID"].tolist()
            )
            dict = []
            dict.append(
                {
                    "CookingHistoryID": new_cooking_history_id,
                    "CookingID": cooking_id,
                    "IssuedDate": datetime.now(),
                }
            )
            df = pd.DataFrame(dict)
            self.__push_table_by_append("CookingHistory", df)

            # 料理に必要な材料分だけ、冷蔵庫の在庫から差し引く
            self.replace_refrigerator(df_rf_after_cooking)

            # 正常に計算終了したのでTrueを返す
            return True
        else:
            # 実際には料理を作ることが出来ないため、計算失敗したということを表すべくFalseを返す。
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

    def __issue_new_id(self, existing_id_list):
        """
        既存のIDのリストを入力に取り、既存のIDとは被らない新しいIDを発行する。
        このとき、なるべく小さい値を新しいIDとして発行する。
        """
        if len(existing_id_list) == 0:
            return 0
        id_max = max(existing_id_list)
        for i in range(id_max):
            if i in existing_id_list:
                continue
            else:
                return i
        return id_max + 1
