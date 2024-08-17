from abc import ABC, abstractmethod
from dataclasses import dataclass, fields
from datetime import datetime

import pandas as pd

from src.datatype.my_enum import PFC
from src.util import fl_eq, fl_ge, g_to_kcal


class DataValidationError(Exception):
    """カスタム例外クラス"""

    pass


@dataclass(frozen=True)
class Validator(ABC):
    """
    本クラスを各dataclassに継承させる。
    各データが有効かを確認するメソッドを定義し、__post_init__でインスタンス生成時に自動でチェックするようにする。
    (継承先をfronzenにするので、mypyの警告が出ないよう本Classもfrozenにする。)
    """

    def __post_init__(self):
        if not self.is_valid_data():
            raise DataValidationError(
                f"{self.__class__.__name__} インスタンスの値が無効です"
            )

    def is_valid_data(self) -> bool:
        """
        総じてデータが有効かどうかを判定する。
        """
        judge1: bool = self._are_all_fields_not_none()
        judge2: bool = self._are_descendant_values_reasonable()
        return judge1 and judge2

    def _are_all_fields_not_none(self) -> bool:
        """ """
        for field in fields(self):
            value = getattr(self, field.name)

            # 継承先の各dataclassの、直接のメンバ変数にNoneが無いかチェック
            if value is None:
                return False

            # 別のdataclassで定義されるメンバ変数があるとき、遡ってNoneが無いかチェック
            if hasattr(value, "_are_all_fields_not_none"):
                if not value._are_all_fields_not_none():
                    return False
        return True

    @abstractmethod
    def _are_values_reasonable(self) -> bool:
        pass

    def _are_descendant_values_reasonable(self) -> bool:
        if not self._are_values_reasonable():
            return False

        for field in fields(self):
            value = getattr(self, field.name)
            # 別のdataclassで定義されるメンバ変数があるとき、遡ってNoneが無いかチェック
            if hasattr(value, "_are_descendant_values_reasonable"):
                if not value._are_descendant_values_reasonable():
                    return False
        return True


@dataclass(frozen=True)  # constで定義する
class RawDataFrame(Validator):
    """
    SQLiteDBの各テーブルに相当するDataFrame
    """

    df_fooddata: pd.DataFrame
    df_cookingfooddata: pd.DataFrame
    df_cooking: pd.DataFrame
    df_cookinghistory: pd.DataFrame
    df_refrigerator: pd.DataFrame
    df_shoppingfooddata: pd.DataFrame
    df_shoppinghistory: pd.DataFrame

    def _are_values_reasonable(self) -> bool:
        # 全てのDataframeに対して、何らか1つ以上のkeyが存在することを確認する。
        for field in fields(self):
            value = getattr(self, field.name)
            if isinstance(value, pd.DataFrame) and len(value.columns) == 0:
                return False
        return True


@dataclass(frozen=True)  # constで定義する
class FoodInfoOfCooking(Validator):
    """
    CookingNutrition型のメンバ変数を定義する型。
    ある料理における、食材ごとの栄養情報を表す。
    (例えばある料理に鶏肉150gが使われていたとしたら、鶏肉150gの栄養情報を表す)
    """

    # ****** Fooddataテーブルに元々存在する情報 ******
    fooddata_id: int
    food_name: str
    standard_unit_name: str
    standard_unit_grams: float

    # ****** 他テーブルと合わせて解釈した情報 ******
    # 標準単位(standard unit)換算の個数
    standard_unit_numbers: float
    # カロリー[kcal]の情報（料理に使う量に対する情報）
    calory_total: float
    caloty_protein: float
    caloty_fat: float
    caloty_carbo: float
    # グラム数[g]の情報（料理に使う量に対する情報）
    grams_total: float
    grams_protein: float
    grams_fat: float
    grams_carbo: float
    # 冷蔵庫に必要なグラム数が存在するか
    is_present_in_refrigerator: bool

    def _are_values_reasonable(self) -> bool:
        calory_pfc = self.caloty_protein + self.caloty_fat + self.caloty_carbo
        grams_pfc = self.grams_protein + self.grams_fat + self.grams_carbo
        ret = (
            # IDが非負である
            self.fooddata_id >= 0
            # 各値が非負である
            and self.calory_total >= 0.0
            and self.caloty_protein >= 0.0
            and self.caloty_fat >= 0.0
            and self.caloty_carbo >= 0.0
            and self.grams_total >= 0.0
            and self.grams_protein >= 0.0
            and self.grams_fat >= 0.0
            and self.grams_carbo >= 0.0
            # PFCの合計がトータルを超えない
            and fl_ge(self.calory_total, calory_pfc)
            and fl_ge(self.grams_total, grams_pfc)
            # PFCのグラム数とカロリーが整合している
            and fl_eq(self.caloty_protein, g_to_kcal(self.grams_protein, PFC.Protein))
            and fl_eq(self.caloty_fat, g_to_kcal(self.grams_fat, PFC.Fat))
            and fl_eq(self.caloty_carbo, g_to_kcal(self.grams_carbo, PFC.Carbo))
            # standard_unit_numbersが整合している
            and fl_eq(
                self.standard_unit_numbers,
                (self.grams_total / self.standard_unit_grams),
            )
        )
        return ret


@dataclass(frozen=True)  # constで定義する
class CookingInfo(Validator):
    """
    CookingNutritionList型の配列要素を定義する型。
    ある料理の栄養情報を表す。
    """

    # ****** Cookingテーブルに元々存在する情報 ******
    cooking_id: int
    cooking_name: str
    is_favorite: bool
    last_update_date: datetime
    description: str

    # ****** 他テーブルと合わせて解釈した情報 ******
    # カロリー[kcal]の情報
    calory_total: float
    caloty_protein: float
    caloty_fat: float
    caloty_carbo: float
    # P/F/Cのグラム数
    grams_protein: float
    grams_fat: float
    grams_carbo: float
    # 食材ごとの栄養情報
    food_attribute: list[FoodInfoOfCooking]
    # 全ての食材が冷蔵庫に必要なグラム数が存在するか
    is_present_in_refrigerator: bool

    def _are_values_reasonable(self) -> bool:
        calory_pfc = self.caloty_protein + self.caloty_fat + self.caloty_carbo
        sum_food_calory = sum([(f.calory_total) for f in self.food_attribute])
        fid_list = [f.fooddata_id for f in self.food_attribute]
        ret = (
            # IDが非負であるである
            self.cooking_id >= 0
            # 各値が非負である
            and self.calory_total >= 0.0
            and self.caloty_protein >= 0.0
            and self.caloty_fat >= 0.0
            and self.caloty_carbo >= 0.0
            and self.grams_protein >= 0.0
            and self.grams_fat >= 0.0
            and self.grams_carbo >= 0.0
            # PFCの合計がトータルを超えない。
            and fl_ge(self.calory_total, calory_pfc)
            # PFCのグラム数とカロリーが整合している
            and fl_eq(self.caloty_protein, g_to_kcal(self.grams_protein, PFC.Protein))
            and fl_eq(self.caloty_fat, g_to_kcal(self.grams_fat, PFC.Fat))
            and fl_eq(self.caloty_carbo, g_to_kcal(self.grams_carbo, PFC.Carbo))
            # 食材の合計カロリーが料理の合計カロリーと一致する
            and fl_eq(self.calory_total, sum_food_calory)
            # 食材のリストの中に同一IDの要素が複数存在しない
            and len(fid_list) == len(set(fid_list))
        )
        return ret


@dataclass(frozen=True)  # constで定義する
class CookingInfoList(Validator):
    """
    登録済みの全ての料理に対する栄養情報を表す型。
    (fronzen=Trueでconst定義してあるが、listの中身は厳密にはconstにならないため注意)
    """

    cookings: list[CookingInfo]

    def _are_values_reasonable(self) -> bool:
        cid_lst = [c.cooking_id for c in self.cookings]
        ret = (
            # 料理のリストの中に同一IDの要素が複数存在しない
            len(cid_lst)
            == len(set(cid_lst))
        )
        return ret
