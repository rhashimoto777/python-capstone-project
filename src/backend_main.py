from datetime import datetime

import pandas as pd

from src.backend_app import backend_common as common
from src.backend_app import fooddata, sqlite_db
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
        fooddata.init()
        self.db_operator = sqlite_db.DataBaseOperator()
        self.raw_df = None
        self.__pull_df_from_db()

    # ________________________________________________________________________________________________________________________
    # global関数群
    def get_raw_df(self):
        """
        classの外側にDBに対応するDataFrameを返す。
        頻繁に呼ばれる関数であるため、動作が遅くならないようにこの関数内でDBからのpull (__pull_df_from_db) は行わない。
        代わりにDBにpushした直後に確実にpullが行われるようにすることで、DBとの乖離無き事を担保する。
        ( そのためには、BackEndOperatorのインスタンスが1つだけである必要がある )
        """
        return self.raw_df

    def get_cooking_details(self):
        """
        Gookingごとの総カロリー・総P/F/C量などの情報を返す。
        出力は辞書型のリストであり、リストの各要素となる辞書には下記の情報が入っている。
            key 'CookingID'         : CookingテーブルのCookingIDと同じ
            key 'CookingAttribute'  : 料理としての合計栄養情報に対応するDataFrame。
                                      ""
            key 'FoodAttribute'     : 料理を構成する食材ごとの栄養情報に対応するDataFrame
        各DataFrameに何が入っているのかはbreakpoint()等を使って確認してください。
        """
        # DB由来のDataFrameを取得
        df_c = self.raw_df.df_cooking
        df_cf = self.raw_df.df_cookingfooddata
        df_f = self.raw_df.df_fooddata

        cooking_id_list = df_c["CookingID"].tolist()
        ret = []
        for c_id in cooking_id_list:
            ########### (1) あるCookingIDを持つCookingを構成する、食材ごとのカロリー情報を生成する ###########
            df_f_attr = df_cf[df_cf["CookingID"] == c_id].merge(df_f, on="FoodDataID")
            df_f_attr["Num_StandardUnit"] = (
                df_f_attr["Grams"] / df_f_attr["StandardUnit_Grams"]
            )

            # P/F/C のグラム情報
            df_f_attr["CookingGrams_Protein"] = (
                df_f_attr["Num_StandardUnit"] * df_f_attr["Grams_Protein"]
            )
            df_f_attr["CookingGrams_Fat"] = (
                df_f_attr["Num_StandardUnit"] * df_f_attr["Grams_Fat"]
            )
            df_f_attr["CookingGrams_Carbo"] = (
                df_f_attr["Num_StandardUnit"] * df_f_attr["Grams_Carbo"]
            )

            # カロリー情報
            df_f_attr["CookingCalory_Total"] = (
                df_f_attr["Num_StandardUnit"] * df_f_attr["Calory_Total"]
            )
            df_f_attr["CookingCalory_Protein"] = (
                df_f_attr["Num_StandardUnit"] * df_f_attr["Calory_Protein"]
            )
            df_f_attr["CookingCalory_Fat"] = (
                df_f_attr["Num_StandardUnit"] * df_f_attr["Calory_Fat"]
            )
            df_f_attr["CookingCalory_Carbo"] = (
                df_f_attr["Num_StandardUnit"] * df_f_attr["Calory_Carbo"]
            )

            # 不要な列を削除する。（他のテーブル等と完全に重複する情報は削除する）
            df_f_attr = df_f_attr.drop(
                columns=[
                    "CookingID",
                    "Calory_Total",
                    "Grams_Protein",
                    "Grams_Fat",
                    "Grams_Carbo",
                    "Calory_Protein",
                    "Calory_Fat",
                    "Calory_Carbo",
                ]
            )

            ########### (2) あるCookingIDを持つCookingを構成する、総カロリー情報を生成する ###########
            # TODO : 同一のCookingIDを持つ要素がCookingテーブル内に複数存在しないことを前提にしているが、どこかで保証する必要がある。
            df_c_attr = df_c[df_c["CookingID"] == c_id]
            df_c_attr = df_c_attr.drop(
                columns=["CookingID", "IsFavorite", "LastUpdateDate", "Description"]
            )
            df_c_attr["CookingGrams_Protein"] = df_f_attr["CookingGrams_Protein"].sum()
            df_c_attr["CookingGrams_Fat"] = df_f_attr["CookingGrams_Fat"].sum()
            df_c_attr["CookingGrams_Carbo"] = df_f_attr["CookingGrams_Carbo"].sum()

            df_c_attr["CookingCalory_Total"] = df_f_attr["CookingCalory_Total"].sum()
            df_c_attr["CookingCalory_Protein"] = df_f_attr[
                "CookingCalory_Protein"
            ].sum()
            df_c_attr["CookingCalory_Fat"] = df_f_attr["CookingCalory_Fat"].sum()
            df_c_attr["CookingCalory_Carbo"] = df_f_attr["CookingCalory_Carbo"].sum()

            ########### (3) 返り値に要素を加える ###########
            dict = {
                "CookingID": c_id,
                "CookingAttribute": df_c_attr,
                "FoodAttribute": df_f_attr,
            }
            ret.append(dict)
        return ret

    def add_cooking(self, df_food_and_grams, df_cooking_attributes):
        """
        「料理の登録（但し実際に食材を消費して料理を作りはしない）」に相当する操作
        """
        # DB上に同じ食材構成のCookingがあるかを判別する。
        cooking_id = self.__judge_same_cooking_already_exist(df_food_and_grams)
        if cooking_id is not None:
            # 既に同じ料理が登録されている状態。
            # 料理を追加で来ていないのでFalseを返し、加えて理由も返す
            return False, "same_cooking_already_exist"
        else:
            cooking_id = self.__issue_new_id(
                self.raw_df.df_cooking["CookingID"].tolist()
            )
            df_cooking_attributes["CookingID"] = cooking_id
            self.__push_df_to_db_by_append("Cooking", df_cooking_attributes)

            df_food_and_grams["CookingID"] = cooking_id
            self.__push_df_to_db_by_append("CookingFoodData", df_food_and_grams)
            # 正常に終了したため、Trueと新しいCookingIDを返す。
            return True, cooking_id

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
            self.__push_df_to_db_by_append("CookingHistory", df)

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
        self.__push_df_to_db_by_replace(TableName.REFRIGERATOR, df_refrigerator)
        return

    # ________________________________________________________________________________________________________________________
    # private関数群
    def __pull_df_from_db(self):
        """
        SQLiteDBをDataFrameに変換し、classのメンバ変数に上書きする。
        """
        self.raw_df = self.db_operator.get_raw_df()
        return

    def __push_df_to_db_by_append(self, table_name, df):
        """
        dfの分だけ新しい行をtableに加える。
        append_dbtable_from_dfを直接呼ばずにこの関数を設けているのは、DBを更新した直後に確実にpullするようにするため。
        """
        self.db_operator.set_table_by_append(table_name, df)
        self.__pull_df_from_db()  # push直後に確実にpullを行う
        return

    def __push_df_to_db_by_replace(self, table_name: TableName, df: pd.DataFrame):
        """
        既存のtableを削除し、dfから生成される新しいtableに置き換える。
        append_dbtable_from_dfを直接呼ばずにこの関数を設けているのは、DBを更新した直後に確実にpullするようにするため。
        """
        self.db_operator.set_table_by_replace(table_name, df)
        self.__pull_df_from_db()  # push直後に確実にpullを行う
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

    def __judge_same_cooking_already_exist(self, df_food_and_grams):
        """
        食材のID・量の一覧から、同じ組成のCookingが既に存在しているかを判別する。
        もし存在している場合、該当するCookingIDを返す。
        存在していない場合、Noneを返す。
        """
        df1 = df_food_and_grams[["FoodDataID", "Grams"]]
        df1["Grams"] = df1["Grams"].astype(float)

        df_c = self.raw_df.df_cooking
        cooking_id_list = df_c["CookingID"].tolist()
        for id in cooking_id_list:
            df_cfd = self.raw_df.df_cookingfooddata
            df_c_id = df_cfd[df_cfd["CookingID"] == id]
            df2 = df_c_id[["FoodDataID", "Grams"]]

            df1_sorted = (
                df1.sort_index(axis=1)
                .sort_values(by=df1.columns.tolist())
                .reset_index(drop=True)
            )
            df2_sorted = (
                df2.sort_index(axis=1)
                .sort_values(by=df2.columns.tolist())
                .reset_index(drop=True)
            )
            are_equal = df1_sorted.equals(df2_sorted)
            if are_equal:
                return id
        return None


# ________________________________________________________________________________________________________________________
if __name__ == "__main__":
    # (デバッグ用)
    backend = BackEndOperator()
