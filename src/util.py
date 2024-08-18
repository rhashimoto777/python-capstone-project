from src.datatype.my_enum import PFC


def fl_eq(in1: float, in2: float) -> bool:
    """
    float型の二値が一致しているか、すなわち in1 == in2 を判定する。
    環境次第では丸め誤差により正確に同じ値にならない場合に備え、多少の幅を設ける。
    (但し、入力の片方が0.0の場合は厳密な一致を判定する)
    """
    in_absmin = min(abs(in1), abs(in2))
    epsilon: float = min(0.001, in_absmin * 0.0001)
    # 上記実装だと、in1 or in2のどちらかが0.0の場合はepsilon = 0.0になるが、それは意図通り

    if epsilon >= abs(in1 - in2):
        return True
    else:
        return False


def fl_ge(in1: float, in2: float) -> bool:
    """
    float型の二値について、in1 >= in2を判定する。
    環境次第では丸め誤差により正確に同じ値にならない場合に備え、多少の幅を設ける。
    (この定義だと、数字上は in1 < in2 のときにも in1 >= in2 と判定される場合があることに注意)
    """
    is_eq = fl_eq(in1, in2)
    if (in1 > in2) or is_eq:
        return True
    else:
        return False


def g_to_kcal(g_val: int | float, type: PFC) -> int | float:
    """
    Protein, Fat, Carboのいずれかについて、グラム[g]からカロリー[kcal]に変換する。
    グラム差分をカロリー差分に変換する用途も想定し、入力のグラムには負の値を許容する。
    """
    match type:
        case PFC.Protein:
            return g_val * 4.0
        case PFC.Fat:
            return g_val * 9.0
        case PFC.Carbo:
            return g_val * 4.0
        case _:
            raise ValueError(f"入力された値 (type=「{type}」)は無効なPFC-enumです")


def backend_system_msg(msg):
    """
    Backend側で用いるシステムメッセージ表示用のprint関数
    """
    print(f"[backend : system-message] {msg}")
    return
