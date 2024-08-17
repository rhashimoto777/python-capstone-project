import pytest

from src import util as u


# _________________________________________________________________________________________________
def test_fl_eq():
    """
    fl_eq()関数の単体テスト
    """

    def test01():
        """
        完全に同じ値同士を比較する
        """
        assert u.fl_eq(100.0, 100.0)
        assert u.fl_eq(0.0, 0.0)
        assert u.fl_eq(-100.0, -100.0)

    def test02():
        """
        元の値同士が大であり、正確には一致しない値を比較する。
        """
        thr1 = 0.00099999999999
        thr2 = 0.00100000000001
        vlist = [100.0, -100.0]
        for v in vlist:
            assert u.fl_eq(v, v + thr1)
            assert u.fl_eq(v, v - thr1)
            assert not u.fl_eq(v, v + thr2)
            assert not u.fl_eq(v, v - thr2)

    def test03():
        """
        元の値同士が小であり、正確には一致しない値を比較する。
        """
        coef1 = 0.000099999999999
        coef2 = 0.000100000000001

        # 入力値が両方とも非ゼロのとき
        vlist = [0.01, -0.01]
        for v in vlist:
            assert u.fl_eq(v, v * (1 + coef1))
            assert u.fl_eq(v * (1 + coef1), v)
            assert not u.fl_eq(v, v * (1 + coef2))
            assert not u.fl_eq(v * (1 + coef2), v)

        # 入力値の片方がゼロのとき
        for v in vlist:
            assert not u.fl_eq(0, v * (1 + coef1))
            assert not u.fl_eq(v * (1 + coef1), 0)

    test01()
    test02()
    test03()
    return


# _________________________________________________________________________________________________
def test_fl_ge():
    """
    fl_ge()関数の単体テスト。
    """

    def test01():
        """
        完全に同じ値が入力された
        """
        assert u.fl_ge(100.0, 100.0)
        assert u.fl_ge(0.0, 0.0)
        assert u.fl_ge(-100.0, -100.0)

    def test02():
        """
        明らかに大小関係がはっきりしている値が入力された
        """
        assert u.fl_ge(100.1, 100.0)
        assert u.fl_ge(0.1, 0.0)
        assert u.fl_ge(-100.0, -100.1)
        assert not u.fl_ge(100.0, 100.1)
        assert not u.fl_ge(0.0, 0.1)
        assert not u.fl_ge(-100.1, -100.0)

    def test03():
        """
        元の値同士が大であり、かつ微小な差しかないとき
        """
        thr1 = 0.00099999999999
        thr2 = 0.00100000000001
        vlist = [100.0, -100.0]
        for v in vlist:
            assert u.fl_ge(v, v + thr1)
            assert u.fl_ge(v, v - thr1)
            assert not u.fl_ge(v, v + thr2)
            assert u.fl_ge(v, v - thr2)

    def test04():
        """
        元の値同士が小であり、正確には一致しない値を比較する。
        """
        coef1 = 0.000099999999999
        coef2 = 0.000100000000001

        # 入力値が両方とも非ゼロのとき
        vlist = [0.01, -0.01]
        for v in vlist:
            assert u.fl_ge(v, v * (1 + coef1))
            assert u.fl_ge(v * (1 + coef1), v)
            assert u.fl_ge(v, v * (1 + coef2)) != (v > 0)
            assert u.fl_ge(v * (1 + coef2), v) == (v > 0)

        # 入力値の片方がゼロのとき
        for v in vlist:
            assert u.fl_ge(0, v * (1 + coef1)) != (v > 0)
            assert u.fl_ge(v * (1 + coef1), 0) == (v > 0)

    test01()
    test02()
    test03()
    test04()
    return


# _________________________________________________________________________________________________
def test_g_to_kcal():
    """
    g_to_kcal関数の単体テスト
    """
    assert u.g_to_kcal(5.0, u.PFC.Protein) == 20.0
    assert u.g_to_kcal(0.0, u.PFC.Protein) == 0.0
    assert u.g_to_kcal(-5.0, u.PFC.Protein) == -20.0

    assert u.g_to_kcal(5.0, u.PFC.Fat) == 45.0
    assert u.g_to_kcal(0.0, u.PFC.Fat) == 0.0
    assert u.g_to_kcal(-5.0, u.PFC.Fat) == -45.0

    assert u.g_to_kcal(5.0, u.PFC.Carbo) == 20.0
    assert u.g_to_kcal(0.0, u.PFC.Carbo) == 0.0
    assert u.g_to_kcal(-5.0, u.PFC.Carbo) == -20.0

    with pytest.raises(ValueError) as e:
        u.g_to_kcal(5.0, 100)
    assert str(e.value) == "入力された値 (type=「100」)は無効なPFC-enumです"
