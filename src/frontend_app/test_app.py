import streamlit as st
import pandas as pd
import sqlite3

# SQLiteデータベースファイルへのパス
db_path = '../../data/user_default/cooking_system.db'  # データベースファイルのパスを指定します

# SQLiteデータベースに接続
conn = sqlite3.connect(db_path)


# SQLクエリを使って'Refrigerator'のテーブルをDataFrameとして読み込む
table_name = 'Refrigerator'  # 取得したいテーブルの名前を指定します
query = f'SELECT * FROM {table_name}'
# Pandasを使ってテーブルを読み込み
ref_df = pd.read_sql_query(query, conn)


# SQLクエリを使って'FoodData'のテーブルをDataFrameとして読み込む
table_name = 'FoodData'  # 取得したいテーブルの名前を指定します
query = f'SELECT * FROM {table_name}'
# Pandasを使ってテーブルを読み込み
food_df = pd.read_sql_query(query, conn)

# Streamlitを使ってDataFrameを表示
st.title('Test')
st.caption('This is the test apprication.')
view_df = pd.merge(ref_df, food_df, how='inner')
st.dataframe(view_df)

# 接続を閉じる
conn.close()
