import sys
import os
from datetime import datetime
import pandas as pd

# subfolderをモジュール検索パスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
subfolder_path = os.path.join(current_dir, 'backend_app')
sys.path.insert(0, subfolder_path)

# backend_appフォルダ内の.pyをインポート
import sqlite_db
import fooddata
import backend_common as common

#________________________________________________________________________________________________________________________
class BackEndOperator():
    def __init__(self):
        common.init() 
        fooddata.init()
        self.db_operator = sqlite_db.DataBaseOperator()
        self.__pull_df_from_db()

    #________________________________________________________________________________________________________________________
    # global関数群
    def get_df_from_db(self):
        """
        classの外側にDBに対応するDataFrameを返す。
        """
        self.__pull_df_from_db()
        return self.df_dict
    
    def add_cooking(self, df_food_and_grams, df_cooking_attributes):
        """
        「料理の登録（但し実際に食材を消費して料理を作りはしない）」に相当する操作
        """
        # DB上に同じ食材構成のCookingがあるかを判別する。
        cooking_id = self.__judge_same_cooking_already_exist(df_food_and_grams)
        if cooking_id != None:
            # 既に同じ料理が登録されている状態。TODO: 何らかユーザーにメッセージで通知する。
            pass
        else:
            cooking_id = self.__issue_new_id(self.df_dict["Cooking"]['CookingID'].tolist())
            df_cooking_attributes["CookingID"] = cooking_id
            self.__push_df_to_db_by_append("Cooking", df_cooking_attributes)

            df_food_and_grams["CookingID"] = cooking_id
            self.__push_df_to_db_by_append("CookingFoodData", df_food_and_grams)
        return cooking_id
    
    def add_cooking_history(self, cooking_id):
        """
        「料理を実際に作る」に相当する操作
        """
        new_cooking_history_id = self.__issue_new_id(self.df_dict["CookingHistory"]['CookingHistoryID'].tolist())

        dict = []
        dict.append({"CookingHistoryID":new_cooking_history_id, "CookingID":cooking_id, "IssuedDate":datetime.now()})
        df = pd.DataFrame(dict)
        self.__push_df_to_db_by_append("CookingHistory",df)

        # TODO : 使った材料の分だけ冷蔵庫から減らす
        return

    #________________________________________________________________________________________________________________________
    # private関数群
    def __pull_df_from_db(self):
        """
        SQLiteDBをDataFrameに変換し、classのメンバ変数に上書きする。
        """
        self.df_dict = self.db_operator.get_df_from_db()
        return
    
    def __push_df_to_db_by_append(self, table_name, df):
        """
        dfの分だけ新しい行をtableに加える。
        append_dbtable_from_dfを直接呼ばずにこの関数を設けているのは、DBを更新した直後に確実にpullするようにするため。
        """
        self.db_operator.append_dbtable_from_df(table_name, df)
        self.__pull_df_from_db()
        return
    
    def __push_df_to_db_by_replace(self, table_name, df):
        """
        既存のtableを削除し、dfから生成される新しいtableに置き換える。
        append_dbtable_from_dfを直接呼ばずにこの関数を設けているのは、DBを更新した直後に確実にpullするようにするため。
        """
        self.db_operator.replace_table_from_df(table_name, df)
        self.__pull_df_from_db()
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
        return id_max+1
    
    def __judge_same_cooking_already_exist(self, df_food_and_grams):
        """
        食材のID・量の一覧から、同じ組成のCookingが既に存在しているかを判別する。
        もし存在している場合、該当するCookingIDを返す。
        存在していない場合、Noneを返す。
        """
        df1 = df_food_and_grams[['FoodDataID', 'Grams']]
        df1['Grams'] = df1['Grams'].astype(float)

        df_c = self.df_dict["Cooking"]
        cooking_id_list = df_c['CookingID'].tolist()
        for id in cooking_id_list:
            df_cfd = self.df_dict["CookingFoodData"]
            df_c_id = df_cfd[df_cfd['CookingID'] == id]
            df2 = df_c_id[['FoodDataID', 'Grams']]

            df1_sorted = df1.sort_index(axis=1).sort_values(by=df1.columns.tolist()).reset_index(drop=True)
            df2_sorted = df2.sort_index(axis=1).sort_values(by=df2.columns.tolist()).reset_index(drop=True)
            are_equal = df1_sorted.equals(df2_sorted)
            if are_equal:
                return id
        return None

#________________________________________________________________________________________________________________________
if __name__ == "__main__":
    # (デバッグ用)
    backend = BackEndOperator()