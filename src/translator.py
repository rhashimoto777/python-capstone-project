import backend_main

class Translator():
    def __init__(self) -> None:
        """
        初期化関数。
        メンバ変数に例えばDataFrameなどの個別データは置かない設計思想とする。
        DataFrameがいつDBからpullされたものか保証できないためだ。
        データ系は全てBackEndOperatorを介して入手し、いつDataがrefreshされるかの制御も
        BackEndOperator側で行う設計思想とする。
        """
        self.backend_op = backend_main.BackEndOperator()
        return
    
    # _______________________________________________________________________
    #                      Get系関数群：DataFrameの取得
    # __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/
    def get_df_all(self) -> dict:
        """ 
        全てのテーブルのDataFrameを包含する辞書を取得する。
        df_dict = get_df_all()
        df_xxx = df_dict["テーブル名"]
        のようにアクセスすれば個別テーブルのDataFrameを取得できる。
        """
        return self.backend_op.get_df_from_db()
    
    def get_df_fooddata(self):
        """ 個別テーブルのDataFrameを取得する。"""
        df_dict = self.backend_op.get_df_from_db()
        return df_dict["FoodData"]

    def get_df_cookingfooddata(self):
        """ 個別テーブルのDataFrameを取得する。"""
        df_dict = self.backend_op.get_df_from_db()
        return df_dict["CookingFoodData"]

    def get_df_cooking(self):
        """ 個別テーブルのDataFrameを取得する。"""
        df_dict = self.backend_op.get_df_from_db()
        return df_dict["Cooking"]

    def get_df_cookinghistory(self):
        """ 個別テーブルのDataFrameを取得する。"""
        df_dict = self.backend_op.get_df_from_db()
        return df_dict["CookingHistory"]

    def get_df_refrigerator(self):
        """ 個別テーブルのDataFrameを取得する。"""
        df_dict = self.backend_op.get_df_from_db()
        return df_dict["Refrigerator"]

    def get_df_shoppingfooddata(self):
        """ 個別テーブルのDataFrameを取得する。"""
        df_dict = self.backend_op.get_df_from_db()
        return df_dict["ShoppingFoodData"]

    def get_df_shoppinghistory(self):
        """ 個別テーブルのDataFrameを取得する。"""
        df_dict = self.backend_op.get_df_from_db()
        return df_dict["ShoppingHistory"]
    
    # _______________________________________________________________________
    #                      Get系関数群：DataFrameの取得
    # __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/
    def get_cooking_details(self):
        """ backend_main.py内の説明を参照 """
        return self.backend_op.get_cooking_details()
    
    # _______________________________________________________________________
    #                      Set系関数群：DataFrameの取得
    # __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/ __/
    def add_cooking(self, df_food_and_grams, df_cooking_attributes):
        """ backend_main.py内の説明を参照 """
        self.backend_op.add_cooking(df_food_and_grams, df_cooking_attributes)
        return 
    
    def add_cooking_history(self, cooking_id):
        """ backend_main.py内の説明を参照 """
        self.backend_op.add_cooking_history(cooking_id)
        return 
    
    def check_possible_to_make_cooking(self, cooking_id):
        """ backend_main.py内の説明を参照 """
        self.backend_op.check_possible_to_make_cooking(cooking_id)
    
    def replace_refrigerator(self, df_refrigerator_new):
        """ backend_main.py内の説明を参照 """
        self.backend_op.replace_refrigerator(df_refrigerator_new)
        return

    

