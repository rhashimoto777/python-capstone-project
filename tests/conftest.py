import os
import sys

from src.backend_app import backend_common as common

# プロジェクトのルートディレクトリを追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def pytest_configure(config):
    """
    全てのテストの計算よりも先に実行される関数
    """
    # PYTEST用のDataBaseに切り替える
    common.init("_PYTEST_")
    print(".\n.\n.\n")
    print(f"......... pytest用のDataBaseに切り替えます。 {common.DB_PATH} .........")
    print(".\n.\n.\n")
    return
