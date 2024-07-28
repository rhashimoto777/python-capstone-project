import sqlite3
import os

import common
def init():
    """
    初回起動時の処理
    """
    _create_db()
    return

def _load_food_data():
    pass


def _create_db():
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
                Calory_Total_Per100g REAL,
                Grams_Protein_Per100g REAL,
                Grams_Fat_Per100g REAL,
                Grams_Carbo_Per100g REAL
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