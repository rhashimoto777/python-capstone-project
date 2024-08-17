from dataclasses import dataclass, replace
from datetime import datetime

import pandas as pd
import pytest

from src.datatype import my_struct


# _____________________________________________________________________________________________
def test_validator_class_01() -> None:
    """
    Validatorクラスの単体テスト。本関数では__post__init__を無効化した状態で
    「_are_all_fields_not_none」「_are_values_reasonable」
    「_are_descendant_values_reasonable」「is_valid_data」をテストする。
    """

    @dataclass(frozen=True)
    class Validator_PostInit_Killed(my_struct.Validator):
        """
        post initを何もしないコードでOverwriteする。
        そうしないとインスタンス生成時にvalid判定が行われるため、狙った試験が出来ない。
        """

        def __post_init__(self):
            pass

    @dataclass(frozen=True)
    class GrandChild(Validator_PostInit_Killed):
        z1: int
        z2: int

        def _are_values_reasonable(self):
            # intのメンバが正であることを条件とする。
            # テストの都合上、入力にNoneを入れても本関数でエラーにならないようにしたいため、型チェックをする。
            ret = True
            if isinstance(self.z1, int) and isinstance(self.z2, int):
                ret = (self.z1 > 0) and (self.z2 > 0)
            return ret

    @dataclass(frozen=True)
    class Child(Validator_PostInit_Killed):
        y1: GrandChild

        def _are_values_reasonable(self):
            return True

    @dataclass(frozen=True)
    class Parent(Validator_PostInit_Killed):
        x1: Child

        def _are_values_reasonable(self):
            return True

    def test01():
        """
        直接のメンバ変数にNoneが含まれているときに
        「_are_all_fields_not_none」「is_valid_data」で検知できるかのテスト
        """
        grandchild_valid = GrandChild(z1=1, z2=1)
        assert grandchild_valid._are_all_fields_not_none()
        assert grandchild_valid.is_valid_data()
        assert grandchild_valid._are_values_reasonable()
        assert grandchild_valid._are_descendant_values_reasonable()
        del grandchild_valid

        grandchild_invalid = GrandChild(z1=1, z2=None)
        assert not grandchild_invalid._are_all_fields_not_none()
        assert not grandchild_invalid.is_valid_data()
        assert grandchild_invalid._are_values_reasonable()
        assert grandchild_invalid._are_descendant_values_reasonable()
        return

    def test02():
        """
        直接のメンバ変数にNoneは無いものの、子・孫の変数にNoneが含まれているときに
        「_are_all_fields_not_none」「is_valid_data」で検知できるかのテスト
        """
        grandchild_valid = GrandChild(z1=1, z2=1)
        child = Child(grandchild_valid)
        parent = Parent(child)
        assert child._are_all_fields_not_none()
        assert child.is_valid_data()
        assert child._are_values_reasonable()
        assert child._are_descendant_values_reasonable()
        assert parent._are_all_fields_not_none()
        assert parent.is_valid_data()
        assert parent._are_values_reasonable()
        assert parent._are_descendant_values_reasonable()
        del grandchild_valid, child, parent

        grandchild_invalid = GrandChild(z1=1, z2=None)
        child = Child(grandchild_invalid)
        parent = Parent(child)
        assert not child._are_all_fields_not_none()
        assert not child.is_valid_data()
        assert child._are_values_reasonable()
        assert child._are_descendant_values_reasonable()
        assert not parent._are_all_fields_not_none()
        assert not parent.is_valid_data()
        assert parent._are_values_reasonable()
        assert parent._are_descendant_values_reasonable()
        return

    def test03():
        """
        直接のメンバ変数に「_are_values_reasonable」に反する値が含まれているときに
        「_are_values_reasonable」「_are_descendant_values_reasonable」「is_valid_data」で検知できるかのテスト
        """
        grandchild_valid = GrandChild(z1=1, z2=1)
        assert grandchild_valid._are_all_fields_not_none()
        assert grandchild_valid._are_values_reasonable()
        assert grandchild_valid._are_descendant_values_reasonable()
        assert grandchild_valid.is_valid_data()
        del grandchild_valid

        grandchild_invalid = GrandChild(z1=1, z2=0)
        assert grandchild_invalid._are_all_fields_not_none()
        assert not grandchild_invalid._are_values_reasonable()
        assert not grandchild_invalid._are_descendant_values_reasonable()
        assert not grandchild_invalid.is_valid_data()
        return

    def test04():
        """
        直接のメンバ変数はValidなものの、子・孫の変数に「_are_values_reasonable」に反する値が含まれているときに
        「_are_descendant_values_reasonable」「_are_descendant_values_reasonable」「is_valid_data」で検知できるかのテスト
        """
        grandchild_valid = GrandChild(z1=1, z2=1)
        child = Child(grandchild_valid)
        parent = Parent(child)
        assert child._are_all_fields_not_none()
        assert child._are_values_reasonable()
        assert child._are_descendant_values_reasonable()
        assert child.is_valid_data()
        assert parent._are_all_fields_not_none()
        assert parent._are_values_reasonable()
        assert parent._are_descendant_values_reasonable()
        assert parent.is_valid_data()
        del grandchild_valid, child, parent

        grandchild_invalid = GrandChild(z1=1, z2=0)
        child = Child(grandchild_invalid)
        parent = Parent(child)
        assert child._are_all_fields_not_none()
        assert child._are_values_reasonable()
        assert not child._are_descendant_values_reasonable()
        assert not child.is_valid_data()
        assert parent._are_all_fields_not_none()
        assert parent._are_values_reasonable()
        assert not parent._are_descendant_values_reasonable()
        assert not parent.is_valid_data()
        return

    test01()
    test02()
    test03()
    test04()
    return


# _____________________________________________________________________________________________
def test_validator_class_02() -> None:
    """
    Validatorクラスの単体テスト。
    本関数では__post__init__が正常に動作しているかをテストする。
    """

    @dataclass(frozen=True)
    class Sample(my_struct.Validator):
        v1: int
        v2: int

        def _are_values_reasonable(self):
            # intのメンバが正であることを条件とする。
            # テストの都合上、入力にNoneを入れても本関数でエラーにならないようにしたいため、型チェックをする。
            ret = True
            if isinstance(self.v1, int) and isinstance(self.v2, int):
                ret = (self.v1 > 0) and (self.v2 > 0)
            return ret

    def test01():
        """
        正常にインスタンス生成が出来ることを確認する。
        """
        try:
            Sample(1, 1)
        except Exception as e:
            pytest.fail(f"インスタンス生成jに失敗しました : {e}")
        return

    def test02():
        """
        要素にNoneを含むインスタンスを生成できないことを確認する。
        """
        instance_name = Sample(1, 1).__class__.__name__
        with pytest.raises(my_struct.DataValidationError) as e:
            Sample(1, None)
        assert str(e.value) == f"{instance_name} インスタンスの値が無効です"
        return

    def test03():
        """
        要素に「_are_values_reasonable」に反する値を含むインスタンスを生成できないことを確認する。
        """
        instance_name = Sample(1, 1).__class__.__name__
        with pytest.raises(my_struct.DataValidationError) as e:
            Sample(1, -1)
        assert str(e.value) == f"{instance_name} インスタンスの値が無効です"
        return

    test01()
    test02()
    test03()
    return


# _____________________________________________________________________________________________
def test_raw_data_frame_class() -> None:
    """
    RawDataFrameクラスのテストを行う。
    """
    valid_df = pd.DataFrame([{"Key": "Data"}])
    empty_df = pd.DataFrame()

    def test01():
        """
        正常にインスタンス生成できることを確認する。
        """
        try:
            valid_instance = my_struct.RawDataFrame(
                df_cooking=valid_df,
                df_cookingfooddata=valid_df,
                df_cookinghistory=valid_df,
                df_fooddata=valid_df,
                df_refrigerator=valid_df,
                df_shoppingfooddata=valid_df,
                df_shoppinghistory=valid_df,
            )
        except Exception as e:
            pytest.fail(f"インスタンス生成jに失敗しました : {e}")
        return valid_instance

    def test02(valid_instance: my_struct.RawDataFrame):
        """
        空のDataframeを含むインスタンス生成できないことを確認する。
        """
        instance_name = "RawDataFrame"
        with pytest.raises(my_struct.DataValidationError) as e:
            replace(valid_instance, df_fooddata=empty_df)
        assert str(e.value) == f"{instance_name} インスタンスの値が無効です"
        return

    valid_instance = test01()
    test02(valid_instance)
    return


# _____________________________________________________________________________________________


def gen_valid_food_info_of_cooking_instance() -> my_struct.FoodInfoOfCooking:
    valid_instance = my_struct.FoodInfoOfCooking(
        # ****** Fooddataテーブルに元々存在する情報 ******
        fooddata_id=0,
        food_name="sample",
        standard_unit_name="sample",
        standard_unit_grams=1.0,
        # ****** 他テーブルと合わせて解釈した情報 ******
        # 標準単位(standard unit)換算の個数
        standard_unit_numbers=10.0,
        # カロリー[kcal]の情報（料理に使う量に対する情報）
        calory_total=20.0,
        caloty_protein=4.0,
        caloty_fat=9.0,
        caloty_carbo=4.0,
        # グラム数[g]の情報（料理に使う量に対する情報）
        grams_total=10.0,
        grams_protein=1.0,
        grams_fat=1.0,
        grams_carbo=1.0,
        # 冷蔵庫に必要なグラム数が存在するか
        is_present_in_refrigerator=True,
    )
    return valid_instance


def test_food_info_of_cooking_class() -> None:
    """
    FoodInfoOfCookingクラスのテスト。
    _are_values_reasonableの条件を全て確認していると大変なので一部だけテストする。
    """
    instance_name = "FoodInfoOfCooking"

    def test01() -> my_struct.FoodInfoOfCooking:
        """
        正常にインスタンス生成できることを確認する。
        """
        try:
            valid_instance: my_struct.FoodInfoOfCooking = (
                gen_valid_food_info_of_cooking_instance()
            )
        except Exception as e:
            pytest.fail(f"インスタンス生成jに失敗しました : {e}")
        return valid_instance

    def test02(valid_instance: my_struct.FoodInfoOfCooking):
        """
        「_are_values_reasonable」の制約が有効かを確認する。
        """
        # IDが非負である
        with pytest.raises(my_struct.DataValidationError) as e:
            replace(valid_instance, fooddata_id=-1)
        assert str(e.value) == f"{instance_name} インスタンスの値が無効です"

        # PFCの合計がトータルを超えない
        with pytest.raises(my_struct.DataValidationError) as e:
            replace(valid_instance, calory_total=10.0)
        assert str(e.value) == f"{instance_name} インスタンスの値が無効です"

        with pytest.raises(my_struct.DataValidationError) as e:
            replace(valid_instance, grams_total=1.0, standard_unit_numbers=1.0)
        assert str(e.value) == f"{instance_name} インスタンスの値が無効です"

        # PFCのグラム数とカロリーが整合している
        with pytest.raises(my_struct.DataValidationError) as e:
            replace(valid_instance, caloty_protein=4.1)
        assert str(e.value) == f"{instance_name} インスタンスの値が無効です"

        with pytest.raises(my_struct.DataValidationError) as e:
            replace(valid_instance, caloty_fat=9.1)
        assert str(e.value) == f"{instance_name} インスタンスの値が無効です"

        with pytest.raises(my_struct.DataValidationError) as e:
            replace(valid_instance, caloty_carbo=4.1)
        assert str(e.value) == f"{instance_name} インスタンスの値が無効です"

        # standard_unit_numbersが整合している
        with pytest.raises(my_struct.DataValidationError) as e:
            replace(valid_instance, standard_unit_numbers=10.1)
        assert str(e.value) == f"{instance_name} インスタンスの値が無効です"
        return

    valid_instance = test01()
    test02(valid_instance)
    return


# _____________________________________________________________________________________________
def gen_valid_cooking_info_instance() -> my_struct.CookingInfo:
    foodinfo_instance = gen_valid_food_info_of_cooking_instance()
    valid_instance = my_struct.CookingInfo(
        # ****** Cookingテーブルに元々存在する情報 ******
        cooking_id=0,
        cooking_name="sample",
        is_favorite=True,
        last_update_date=datetime.now(),
        description="aaaaa",
        # ****** 他テーブルと合わせて解釈した情報 ******
        # カロリー[kcal]の情報
        calory_total=40.0,
        caloty_protein=8.0,
        caloty_fat=18.0,
        caloty_carbo=8.0,
        # P/F/Cのグラム数
        grams_protein=2.0,
        grams_fat=2.0,
        grams_carbo=2.0,
        # 食材ごとの栄養情報
        food_attribute=[
            foodinfo_instance,
            replace(foodinfo_instance, fooddata_id=1),
        ],
        # 全ての食材が冷蔵庫に必要なグラム数が存在するか
        is_present_in_refrigerator=True,
    )
    return valid_instance


def test_cooking_info_class() -> None:
    """
    CookingInfoクラスのテスト。
    _are_values_reasonableの条件を全て確認していると大変なので一部だけテストする。
    """
    instance_name = "CookingInfo"

    foodinfo_instance: my_struct.FoodInfoOfCooking = (
        gen_valid_food_info_of_cooking_instance()
    )

    def test01() -> my_struct.CookingInfo:
        """
        正常にインスタンス生成できることを確認する。
        """
        try:
            valid_instance: my_struct.CookingInfo = gen_valid_cooking_info_instance()
        except Exception as e:
            pytest.fail(f"インスタンス生成jに失敗しました : {e}")
        return valid_instance

    def test02(valid_instance: my_struct.CookingInfo):
        """
        「_are_values_reasonable」の制約が有効かを確認する。
        """
        # IDが非負である
        with pytest.raises(my_struct.DataValidationError) as e:
            replace(valid_instance, cooking_id=-1)
        assert str(e.value) == f"{instance_name} インスタンスの値が無効です"

        # PFCの合計がトータルを超えない
        with pytest.raises(my_struct.DataValidationError) as e:
            replace(valid_instance, calory_total=10.0)
        assert str(e.value) == f"{instance_name} インスタンスの値が無効です"

        # PFCのグラム数とカロリーが整合している
        with pytest.raises(my_struct.DataValidationError) as e:
            replace(valid_instance, caloty_protein=8.1)
        assert str(e.value) == f"{instance_name} インスタンスの値が無効です"

        with pytest.raises(my_struct.DataValidationError) as e:
            replace(valid_instance, caloty_fat=18.1)
        assert str(e.value) == f"{instance_name} インスタンスの値が無効です"

        with pytest.raises(my_struct.DataValidationError) as e:
            replace(valid_instance, caloty_carbo=8.1)
        assert str(e.value) == f"{instance_name} インスタンスの値が無効です"

        # 食材の合計カロリーが料理の合計カロリーと一致する
        with pytest.raises(my_struct.DataValidationError) as e:
            replace(valid_instance, calory_total=40.1)
        assert str(e.value) == f"{instance_name} インスタンスの値が無効です"

        # 食材のリストの中に同一IDの要素が複数存在しない
        with pytest.raises(my_struct.DataValidationError) as e:
            replace(
                valid_instance, food_attribute=[foodinfo_instance, foodinfo_instance]
            )
        assert str(e.value) == f"{instance_name} インスタンスの値が無効です"
        return

    valid_instance = test01()
    test02(valid_instance)
    return


# _____________________________________________________________________________________________
def test_cooking_info_list_class() -> None:
    """
    CookingInfoListクラスのテスト
    """
    instance_name = "CookingInfoList"
    cooking_info = gen_valid_cooking_info_instance()

    def test01():
        """
        正常にインスタンス生成できることを確認する。
        """
        try:
            my_struct.CookingInfoList(
                [cooking_info, replace(cooking_info, cooking_id=1)]
            )
        except Exception as e:
            pytest.fail(f"インスタンス生成jに失敗しました : {e}")
        return

    def test02():
        """
        「_are_values_reasonable」の制約が有効かを確認する。
        """
        # 同一IDの要素が複数存在しない
        with pytest.raises(my_struct.DataValidationError) as e:
            my_struct.CookingInfoList([cooking_info, cooking_info])
        assert str(e.value) == f"{instance_name} インスタンスの値が無効です"
        return

    test01()
    test02()
    return
