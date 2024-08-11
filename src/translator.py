from src import backend_main

# モジュール内のトップレベルのコードは、モジュールの初回import時にしか行われない。
# translator.pyは様々な.pyファイルからimportされるが、BackEndOperator()のインスタンス生成はシステム全体を通して1回しか実行されない。
backend_op = backend_main.BackEndOperator()

def init():
    global backend_op
    backend_op = backend_main.BackEndOperator()
    
# _______________________________________________________________________
#                      Get系関数群：DataFrameの取得
# __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/
def get_df_all() -> dict:
    """ 
    全てのテーブルのDataFrameを包含する辞書を取得する。
    df_dict = get_df_all()
    df_xxx = df_dict["テーブル名"]
    のようにアクセスすれば個別テーブルのDataFrameを取得できる。
    """
    return backend_op.get_df_from_db()

def get_df_fooddata():
    """ 個別テーブルのDataFrameを取得する。"""
    df_dict = backend_op.get_df_from_db()
    return df_dict["FoodData"]

def get_df_cookingfooddata():
    """ 個別テーブルのDataFrameを取得する。"""
    df_dict = backend_op.get_df_from_db()
    return df_dict["CookingFoodData"]

def get_df_cooking():
    """ 個別テーブルのDataFrameを取得する。"""
    df_dict = backend_op.get_df_from_db()
    return df_dict["Cooking"]

def get_df_cookinghistory():
    """ 個別テーブルのDataFrameを取得する。"""
    df_dict = backend_op.get_df_from_db()
    return df_dict["CookingHistory"]

def get_df_refrigerator():
    """ 個別テーブルのDataFrameを取得する。"""
    df_dict = backend_op.get_df_from_db()
    return df_dict["Refrigerator"]

def get_df_shoppingfooddata():
    """ 個別テーブルのDataFrameを取得する。"""
    df_dict = backend_op.get_df_from_db()
    return df_dict["ShoppingFoodData"]

def get_df_shoppinghistory():
    """ 個別テーブルのDataFrameを取得する。"""
    df_dict = backend_op.get_df_from_db()
    return df_dict["ShoppingHistory"]

# _______________________________________________________________________
#                      Get系関数群：各種解釈情報の取得
# __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/
def get_cooking_details():
    """ backend_main.py内の説明を参照 """
    return backend_op.get_cooking_details()

def check_possible_to_make_cooking(cooking_id):
    """ backend_main.py内の説明を参照 """
    backend_op.check_possible_to_make_cooking(cooking_id)

# _______________________________________________________________________
#                      Set系関数群：何らかDBに値を書き込む操作
# __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/
def add_cooking(df_food_and_grams, df_cooking_attributes):
    """ backend_main.py内の説明を参照 """
    is_success, msg = backend_op.add_cooking(df_food_and_grams, df_cooking_attributes)
    return is_success, msg

def add_cooking_history(cooking_id):
    """ backend_main.py内の説明を参照 """
    backend_op.add_cooking_history(cooking_id)
    return 

def replace_refrigerator(df_refrigerator_new):
    """ backend_main.py内の説明を参照 """
    backend_op.replace_refrigerator(df_refrigerator_new)
    return

    

