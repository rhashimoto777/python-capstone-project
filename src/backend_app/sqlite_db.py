import backend_common as common
import sqlite3
import os
import json
import pandas as pd
from contextlib import contextmanager

class DataBaseOperator:
    def __init__(self) -> None:
        self.__create_db()
        self.__load_fooddata_json()
        return
    
    #________________________________________________________________________________________________________________________
    # global関数群
    def get_df_from_db(self):
        """
        SQLiteDBからDataFrameを取得する。
        DBのtableそれぞれをそのままDataFrameに変換し、辞書型で返す。
        """
        df_dict = {}
        with self.__get_connection_to_db() as conn:
            # TODO: この場所でtablesをハードコーディングするのは綺麗ではない。（いろんなところで同じ定義が必要になりそうなので、何らか共通化したい）
            tables = ['FoodData', 'FoodAmount', 'CookingHistory', 'Cooking', 'CookingFoodAmount', 'Refrigerator', 'ShoppingHistory', 'ShoppingFoodAmount']

            # DataFrameに変換
            for table_name in tables:
                query = f"SELECT * FROM {table_name} ORDER BY ROWID DESC LIMIT 5"
                df = pd.read_sql_query(query, conn)
                df_dict[table_name] = df
        return df_dict
    
    def write_db_from_df(self, table_name, df):
        """
        DataFrameをDBに書き込む
        """
        try:
            with self.__get_connection_to_db() as conn:
                df.to_sql(table_name, conn, if_exists='append', index=False)
        except Exception as e:
            print(f'Error : {e}')
        return

    #________________________________________________________________________________________________________________________
    # private関数群
    @contextmanager
    def __get_connection_to_db(self):
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

    def __load_fooddata_json(self):
        """
        FoodDataのjsonを読み込み、DBのFoodDataテーブルに書き込む。
        起動時1回しか読まない想定なのでprivate関数にしておく。
        """
        # jsonの読み込み
        os.chdir(common.FOODDATA_JSON_PATH)
        with open(common.FOODDATA_JSON_FILENAME, "r", encoding='utf-8') as file:
            data = json.load(file)
        df = pd.DataFrame(data)

        # DBのFoodDataテーブルへの書き込み
        with self.__get_connection_to_db() as conn:
            df.to_sql('FoodData', conn, if_exists='append', index=False)
        return


    def __create_db(self):
        """
        DBを作成する。DBが既に存在する場合は何もしない。
        """
        os.makedirs(common.DB_PATH, exist_ok=True)

        # データベースを作成または接続
        with self.__get_connection_to_db() as conn:
            cursor = conn.cursor()

            # FoodDataテーブルの作成
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS FoodData (
                    FoodDataID INTEGER PRIMARY KEY,
                    FoodName TEXT,
                    Calory_Total REAL,
                    Grams_Protein REAL,
                    Grams_Fat REAL,
                    Grams_Carbo REAL,
                    StandardUnit_Name TEXT,
                    StandardUnit_Grams REAL
                )
            ''')

            # FoodAmountテーブルの作成
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS FoodAmount (
                    FoodAmountID INTEGER PRIMARY KEY,
                    FoodDataID INTEGER,
                    Grams_Total REAL,
                    Grams_Protein REAL,
                    Grams_Fat REAL,
                    Grams_Carbo REAL,
                    Calory_Total REAL,
                    Calory_Protein REAL,
                    Calory_Fat REAL,
                    Calory_Carbo REAL,
                    FOREIGN KEY (FoodDataID) REFERENCES FoodData(FoodDataID)
                )
            ''')

            # CookingHistoryテーブルの作成
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS CookingHistory (
                    CookingHistoryID INTEGER PRIMARY KEY,
                    CookingID INTEGER,
                    IssuedDate DATETIME,
                    FOREIGN KEY (CookingID) REFERENCES Cooking(CookingID)
                )
            ''')

            # Cookingテーブルの作成
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Cooking (
                    CookingID INTEGER PRIMARY KEY,
                    CookingName TEXT,
                    IsFavorite BOOLEAN,
                    LastUpdateDate DATETIME,
                    Description TEXT
                )
            ''')

            # CookingFoodAmountテーブルの作成
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS CookingFoodAmount (
                    CookingID INTEGER,
                    FoodAmountID INTEGER,
                    FOREIGN KEY (CookingID) REFERENCES Cooking(CookingID),
                    FOREIGN KEY (FoodAmountID) REFERENCES FoodAmount(FoodAmountID)
                )
            ''')

            # Refrigeratorテーブルの作成
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Refrigerator (
                    FoodAmountID INTEGER,
                    FOREIGN KEY (FoodAmountID) REFERENCES FoodAmount(FoodAmountID)
                )
            ''')

            # ShoppingHistoryテーブルの作成
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ShoppingHistory (
                    ShoppingHistoryID INTEGER PRIMARY KEY,
                    IssuedDate DATETIME
                )
            ''')

            # ShoppingFoodAmountテーブルの作成
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ShoppingFoodAmount (
                    ShoppingID INTEGER,
                    FoodAmountID INTEGER,
                    FOREIGN KEY (ShoppingID) REFERENCES ShoppingHistory(ShoppingHistoryID),
                    FOREIGN KEY (FoodAmountID) REFERENCES FoodAmount(FoodAmountID)
                )
            ''')
        return