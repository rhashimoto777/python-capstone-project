import backend_common as common
import sqlite3
import os
import json
import pandas as pd
from contextlib import contextmanager
import shutil

class DataBaseOperator:
    def __init__(self) -> None:
        self.__restore_db_file_from_backup()
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
            tables = ['FoodData', 'CookingFoodData', 'Cooking', 'CookingHistory', 'Refrigerator', 'ShoppingFoodData', 'ShoppingHistory']

            # DataFrameに変換
            for table_name in tables:
                query = f"SELECT * FROM {table_name}"
                df = pd.read_sql_query(query, conn)
                df_dict[table_name] = df
        return df_dict
    
    def replace_table_from_df(self, table_name, df):
        """
        DataFrameをDBに書き込む (既存のtableを削除し、新しいtableに置き換える)
        """
        try:
            with self.__get_connection_to_db() as conn:
                df.to_sql(table_name, conn, if_exists='replace', index=False)
        except Exception as e:
            print(f'Error : {e}')
        return
    
    def append_dbtable_from_df(self, table_name, df):
        """
        DataFrameをDBに書き込む (既存のtableは残し、dfの分だけ新しい行を追加する)
        """
        try:
            with self.__get_connection_to_db() as conn:
                df.to_sql(table_name, conn, if_exists='append', index=False)
        except Exception as e:
            print(f'Error : {e}')
        return

    #________________________________________________________________________________________________________________________
    # private関数群
    @staticmethod
    def __restore_db_file_from_backup():
        """
        DBのバックアップファイルが存在し、かつcooking_system.dbが存在しないとき、バックアップからコピーしてcooking_system.dbを作る。
        「cooking_system.dbは実行状態に依存して頻繁に変わるため.gitignoreに登録しているが、一方でGitHub上にデフォルトのDBは登録しておきたい」
        という背景から本関数を用意している。 (主に初回起動時に1回だけcallすることを想定している)
        """
        src = os.path.join(common.DB_PATH, common.DB_BACKUP_FILENAME)   # コピー元ファイル (=バックアップファイル)
        dst = os.path.join(common.DB_PATH, common.DB_FILENAME)          # コピー先ファイル
        is_src_file_exist = os.path.exists(src)
        is_dst_file_exist = os.path.exists(dst)

        if is_src_file_exist and (not is_dst_file_exist):
            # バックアップファイルが存在し、かつコピー先ファイルが存在しない場合のみ、バックアップファイルをコピーしてDBファイルを作る
            shutil.copy(src, dst) 
            common.system_msg_print(f'Restored "{common.DB_FILENAME}" from "{common.DB_BACKUP_FILENAME}"')
        return

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

        また、P/F/Cのグラム数を単純に4/9/4倍すると、P/F/Cの合計カロリーが総カロリーを超えることがある。
        これは明らかに不整合であり、「P/F/Cのグラム数」「P/F/Cのカロリー」「食材の総カロリー」の
        いずれかを補正する必要があるが、総カロリーを補正する方針とする。
        """
        # jsonの読み込み
        os.chdir(common.FOODDATA_JSON_PATH)
        with open(common.FOODDATA_JSON_FILENAME, "r", encoding='utf-8') as file:
            data = json.load(file)
        df = pd.DataFrame(data)
        
        # Protein / Fat / Carbo由来のカロリーを計算する
        df['Calory_Protein'] = df['Grams_Protein'] * 4.0
        df['Calory_Fat']     = df['Grams_Fat']     * 9.0
        df['Calory_Carbo']   = df['Grams_Carbo']   * 4.0

        # P/F/Cの合計カロリーが総カロリーを超えないよう、総カロリーを補正する。
        df['tmp_Calory_PFC'] = df['Calory_Protein'] + df['Calory_Fat'] + df['Calory_Carbo']
        mask = df['tmp_Calory_PFC'] > df['Calory_Total']
        for i in range(len(df[mask])):
            # システムメッセージを表示する
            elem = df[mask].iloc[i]
            msg =  f'FoodDataテーブルにおいて、'
            msg += f'「{elem.loc["FoodName"]}」の「PFC合計カロリー({elem.loc["tmp_Calory_PFC"]:.1f})」が'
            msg += f'「食材の総カロリー({elem.loc["Calory_Total"]:.1f})」を超えています。'
            msg += f'値の整合のため、「総カロリー」を{elem.loc["tmp_Calory_PFC"]:.1f}に置き換えます。'
            common.system_msg_print(msg)
        df.loc[mask, 'Calory_Total'] = df.loc[mask, 'tmp_Calory_PFC']
        df = df.drop(columns=['tmp_Calory_PFC'])

        # DBのFoodDataテーブルへの書き込み
        with self.__get_connection_to_db() as conn:
            df.to_sql('FoodData', conn, if_exists='replace', index=False)
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
                    Calory_Protein REAL,
                    Calory_Fat REAL,
                    Calory_Carbo REAL,
                    StandardUnit_Name TEXT,
                    StandardUnit_Grams REAL
                )
            ''')

            # CookingFoodDataテーブルの作成
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS CookingFoodData (
                    CookingID INTEGER,
                    FoodDataID INTEGER,
                    Grams REAL,
                    FOREIGN KEY (CookingID) REFERENCES Cooking(CookingID),
                    FOREIGN KEY (FoodDataID) REFERENCES FoodData(FoodDataID)
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

            # CookingHistoryテーブルの作成
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS CookingHistory (
                    CookingHistoryID INTEGER PRIMARY KEY,
                    CookingID INTEGER,
                    IssuedDate DATETIME,
                    FOREIGN KEY (CookingID) REFERENCES Cooking(CookingID)
                )
            ''')

            # Refrigeratorテーブルの作成
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Refrigerator (
                    FoodDataID INTEGER UNIQUE,
                    Grams REAL,
                    FOREIGN KEY (FoodDataID) REFERENCES FoodData(FoodDataID)
                )
            ''')

            # ShoppingFoodDataテーブルの作成
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ShoppingFoodData (
                    ShoppingHistoryID INTEGER,
                    FoodDataID INTEGER,
                    Grams REAL,
                    FOREIGN KEY (ShoppingHistoryID) REFERENCES ShoppingHistory(ShoppingHistoryID),
                    FOREIGN KEY (FoodDataID) REFERENCES FoodData(FoodDataID)
                )
            ''')

            # ShoppingHistoryテーブルの作成
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ShoppingHistory (
                    ShoppingHistoryID INTEGER PRIMARY KEY,
                    IssuedDate DATETIME
                )
            ''')
        return