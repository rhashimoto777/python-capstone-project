import json
import os
import shutil
import sqlite3
from contextlib import contextmanager

import pandas as pd

from src.backend_app import backend_common as common
from src.datatype.my_enum import TableName
from src.datatype.my_struct import DataValidationError, RawDataFrame


# _________________________________________________________________________________________________________________________
class DataBaseCommon:
    @contextmanager
    def get_connection_to_db(self):
        """
        DBに接続する際には毎回「作業ディレクトリをDB_PATHに変えて」「DB_FILENAMEにconnectして」「conn.close()する」処理が必要だが、
        それらを呼び出し元で複数回定義すると煩雑だがバグの素となり得る。（どこかで上記のいずれかを忘れたり誤記するかもしれない）
        そのため、with句を用いてDB接続する際に、同時に上記操作が全て行えるように本関数を定義している。
        """
        os.chdir(common.DB_PATH)
        conn = sqlite3.connect(common.DB_FILENAME)
        try:
            yield conn
        finally:
            conn.close()


# _________________________________________________________________________________________________________________________
class DataBaseOperator(DataBaseCommon):
    """
    「DataBaseからの情報の取得」と「DataBaseの更新」を主に行う。
    「DataBaseの作成/削除」は別クラスに分け、本クラスに合成する。
    """

    def __init__(self) -> None:
        common.init()  # pytest用。既にどこかでinit()が呼ばれていれば何もしない。
        self.creator = DataBaseCreator()
        return

    def get_raw_df(self) -> RawDataFrame:
        """
        DBから生のDataFramwを取得する
        """

        # 関数内の共通関数定義
        def read_table(table_name: TableName) -> pd.DataFrame:
            query = f"SELECT * FROM {table_name.value}"
            return pd.read_sql_query(query, conn)

        # DBからDataFrameを読み込む。
        df_dict = {}
        table_names = [
            TableName.FOODDATA,
            TableName.COOKING,
            TableName.COOKING_FOOD_DATA,
            TableName.COOKING_HISTORY,
            TableName.REFRIGERATOR,
            TableName.SHOPPING_FOOD_DATA,
            TableName.SHOPPING_HISTORY,
        ]
        with self.get_connection_to_db() as conn:
            for name in table_names:
                try:
                    df_dict[name] = read_table(name)
                except Exception as e:
                    raise Exception(f"Failed to read table {name}: {e}")

        # RawDataFrameデータクラスを生成する。
        try:
            raw_df = RawDataFrame(
                df_fooddata=df_dict[TableName.FOODDATA],
                df_cooking=df_dict[TableName.COOKING],
                df_cookingfooddata=df_dict[TableName.COOKING_FOOD_DATA],
                df_cookinghistory=df_dict[TableName.COOKING_HISTORY],
                df_refrigerator=df_dict[TableName.REFRIGERATOR],
                df_shoppingfooddata=df_dict[TableName.SHOPPING_FOOD_DATA],
                df_shoppinghistory=df_dict[TableName.SHOPPING_HISTORY],
            )
        except DataValidationError as e:
            raise DataValidationError(f"Data Validation Error: {e}")
        return raw_df

    def set_table_by_replace(self, table_name: TableName, df: pd.DataFrame):
        """
        DataFrameをDataBaseのtableに書き込む。
        このとき、既存のtableを削除し新しいtableに置き換える。
        """
        try:
            with self.get_connection_to_db() as conn:
                df.to_sql(table_name.value, conn, if_exists="replace", index=False)
        except Exception as e:
            print(f"Error : {e}")
        return

    def set_table_by_append(self, table_name: TableName, df: pd.DataFrame):
        """
        DataFrameをDataBaseのtableに書き込む。
        このとき、既存のtableは残しdfの分だけ新しい行を追加する。
        """
        try:
            with self.get_connection_to_db() as conn:
                df.to_sql(table_name.value, conn, if_exists="append", index=False)
        except Exception as e:
            print(f"Error : {e}")
        return


# _________________________________________________________________________________________________________________________
class DataBaseCreator(DataBaseCommon):
    """
    「DataBaseの作成/削除」を行うメソッドを集めたクラス。
    """

    def __init__(self) -> None:
        common.init()  # pytest用。既にどこかでinit()が呼ばれていれば何もしない。
        self.__restore_db_file_from_backup()
        self.__create_db()
        self.__load_fooddata_json()

    @staticmethod
    def __restore_db_file_from_backup():
        """
        DBのバックアップファイルが存在し、かつcooking_system.dbが存在しないとき、バックアップからコピーしてcooking_system.dbを作る。
        「cooking_system.dbは実行状態に依存して頻繁に変わるため.gitignoreに登録しているが、一方でGitHub上にデフォルトのDBは登録しておきたい」
        という背景から本関数を用意している。 (主に初回起動時に1回だけcallすることを想定している)
        """
        # コピー元ファイル (=バックアップファイル)
        src = os.path.join(common.DB_PATH, common.DB_BACKUP_FILENAME)
        # コピー先ファイル
        dst = os.path.join(common.DB_PATH, common.DB_FILENAME)

        is_src_file_exist = os.path.exists(src)
        is_dst_file_exist = os.path.exists(dst)

        if is_src_file_exist and (not is_dst_file_exist):
            # バックアップファイルが存在し、かつコピー先ファイルが存在しない場合のみ、
            # バックアップファイルをコピーしてDBファイルを作る
            shutil.copy(src, dst)
            common.system_msg_print(
                f'Restored "{common.DB_FILENAME}" from "{common.DB_BACKUP_FILENAME}"'
            )
        return

    def __load_fooddata_json(self):
        """
        FoodDataのjsonを読み込み、DBのFoodDataテーブルに書き込む。
        起動時1回しか読まない想定なのでprivate関数にしておく。

        また、P/F/Cのグラム数を単純に4/9/4倍すると、P/F/Cの合計カロリーが総カロリーを超えることがある。
        これは明らかに不整合であり、「P/F/Cのグラム数」「P/F/Cのカロリー」「食材の総カロリー」の
        いずれかを補正する必要があるが、総カロリーを補正する方針とする。
        """
        # jsonの読み込み
        os.chdir(common.FOODDATA_JSON_PATH)
        with open(common.FOODDATA_JSON_FILENAME, "r", encoding="utf-8") as file:
            data = json.load(file)
        df = pd.DataFrame(data)

        # Protein / Fat / Carbo由来のカロリーを計算する
        df["Calory_Protein"] = df["Grams_Protein"] * 4.0
        df["Calory_Fat"] = df["Grams_Fat"] * 9.0
        df["Calory_Carbo"] = df["Grams_Carbo"] * 4.0

        # P/F/Cの合計カロリーが総カロリーを超えないよう、総カロリーを補正する。
        df["tmp_Calory_PFC"] = (
            df["Calory_Protein"] + df["Calory_Fat"] + df["Calory_Carbo"]
        )
        mask = df["tmp_Calory_PFC"] > df["Calory_Total"]
        for i in range(len(df[mask])):
            # システムメッセージを表示する
            elem = df[mask].iloc[i]
            msg = "FoodDataテーブルにおいて、"
            msg += f'「{elem.loc["FoodName"]}」の「PFC合計カロリー({elem.loc["tmp_Calory_PFC"]:.1f})」が'
            msg += (
                f'「食材の総カロリー({elem.loc["Calory_Total"]:.1f})」を超えています。'
            )
            msg += f'値の整合のため、「総カロリー」を{elem.loc["tmp_Calory_PFC"]:.1f}に置き換えます。'
            common.system_msg_print(msg)
        df.loc[mask, "Calory_Total"] = df.loc[mask, "tmp_Calory_PFC"]
        df = df.drop(columns=["tmp_Calory_PFC"])

        # DBのFoodDataテーブルへの書き込み
        with self.get_connection_to_db() as conn:
            df.to_sql("FoodData", conn, if_exists="replace", index=False)
        return

    def __create_db(self):
        """
        DBを作成する。DBが既に存在する場合は何もしない。
        """
        os.makedirs(common.DB_PATH, exist_ok=True)

        # データベースを作成または接続
        with self.get_connection_to_db() as conn:
            cursor = conn.cursor()

            # FoodDataテーブルの作成
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {TableName.FOODDATA.value} (
                    FoodDataID INTEGER PRIMARY KEY,
                    FoodName TEXT,
                    Calory_Total REAL,
                    Grams_Protein REAL,
                    Grams_Fat REAL,
                    Grams_Carbo REAL,
                    Calory_Protein REAL,
                    Calory_Fat REAL,
                    Calory_Carbo REAL,
                    StandardUnit_Name TEXT,
                    StandardUnit_Grams REAL
                )
            """
            )

            # CookingFoodDataテーブルの作成
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {TableName.COOKING_FOOD_DATA.value} (
                    CookingID INTEGER,
                    FoodDataID INTEGER,
                    Grams REAL,
                    FOREIGN KEY (CookingID) REFERENCES Cooking(CookingID),
                    FOREIGN KEY (FoodDataID) REFERENCES FoodData(FoodDataID)
                )
            """
            )

            # Cookingテーブルの作成
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {TableName.COOKING.value} (
                    CookingID INTEGER PRIMARY KEY,
                    CookingName TEXT,
                    IsFavorite BOOLEAN,
                    LastUpdateDate DATETIME,
                    Description TEXT
                )
            """
            )

            # CookingHistoryテーブルの作成
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {TableName.COOKING_HISTORY.value} (
                    CookingHistoryID INTEGER PRIMARY KEY,
                    CookingID INTEGER,
                    IssuedDate DATETIME,
                    FOREIGN KEY (CookingID) REFERENCES Cooking(CookingID)
                )
            """
            )

            # Refrigeratorテーブルの作成
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {TableName.REFRIGERATOR.value} (
                    FoodDataID INTEGER UNIQUE,
                    Grams REAL,
                    FOREIGN KEY (FoodDataID) REFERENCES FoodData(FoodDataID)
                )
            """
            )

            # ShoppingFoodDataテーブルの作成
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {TableName.SHOPPING_FOOD_DATA.value} (
                    ShoppingHistoryID INTEGER,
                    FoodDataID INTEGER,
                    Grams REAL,
                    FOREIGN KEY (ShoppingHistoryID) REFERENCES ShoppingHistory(ShoppingHistoryID),
                    FOREIGN KEY (FoodDataID) REFERENCES FoodData(FoodDataID)
                )
            """
            )

            # ShoppingHistoryテーブルの作成
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {TableName.SHOPPING_HISTORY.value} (
                    ShoppingHistoryID INTEGER PRIMARY KEY,
                    IssuedDate DATETIME
                )
            """
            )
