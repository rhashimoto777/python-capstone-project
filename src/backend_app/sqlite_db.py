import backend_common as common
import sqlite3
import os
import json
import pandas as pd

class DataBaseOperator:
    def __init__(self) -> None:
        self.__create_db()
        self.__load_fooddata_json()
        return

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
        print(df)

        # DBのFoodDataテーブルへの書き込み
        os.chdir(common.DB_PATH)
        with sqlite3.connect(common.DB_FILENAME) as conn:
            df.to_sql('FoodData', conn, if_exists='append', index=False)
        return


    def __create_db(self):
        """
        DBを作成する。DBが既に存在する場合は何もしない。
        """
        os.makedirs(common.DB_PATH, exist_ok=True)
        os.chdir(common.DB_PATH)

        # データベースを作成または接続
        with sqlite3.connect(common.DB_FILENAME) as conn:
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