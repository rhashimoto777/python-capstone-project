import pytest

from src.backend_app import common_info as common


@pytest.fixture(autouse=True)
def setup_and_teardown():
    # グローバル変数のバックアップ
    ROOT_PATH = common.ROOT_DIR
    DB_PATH = common.DB_DIR
    USER_PATH = common.USER_LIST_DIR
    CURRENT_USER_FILE_DIR = common.CURRENT_USER_FILE_DIR
    CURRENT_USER_FILENAME = common.CURRENT_USER_FILENAME
    DB_FILENAME = common.DB_FILENAME
    DB_BACKUP_FILENAME = common.DB_BACKUP_FILENAME
    FOODDATA_JSON_PATH = common.FOODDATA_JSON_DIR
    FOODDATA_JSON_FILENAME = common.FOODDATA_JSON_FILENAME
    USER_ID = common.USER_ID
    INIT_FINISH = common.INIT_FINISH

    # テスト前の初期化
    return_to_initial()
    all_global_are_initial()

    yield

    # テスト後に元の値に戻す
    common.ROOT_DIR = ROOT_PATH
    common.USER_LIST_DIR = USER_PATH
    common.CURRENT_USER_FILE_DIR = CURRENT_USER_FILE_DIR
    common.CURRENT_USER_FILENAME = CURRENT_USER_FILENAME
    common.DB_DIR = DB_PATH
    common.DB_FILENAME = DB_FILENAME
    common.DB_BACKUP_FILENAME = DB_BACKUP_FILENAME
    common.FOODDATA_JSON_DIR = FOODDATA_JSON_PATH
    common.FOODDATA_JSON_FILENAME = FOODDATA_JSON_FILENAME
    common.USER_ID = USER_ID
    common.INIT_FINISH = INIT_FINISH


def all_global_are_initial():
    """
    全てのグローバル変数が初期値であることを確認する。
    """
    assert common.ROOT_DIR is None
    assert common.USER_LIST_DIR is None
    assert common.CURRENT_USER_FILE_DIR is None
    assert common.CURRENT_USER_FILENAME is None
    assert common.DB_DIR is None
    assert common.DB_FILENAME is None
    assert common.DB_BACKUP_FILENAME is None
    assert common.FOODDATA_JSON_DIR is None
    assert common.FOODDATA_JSON_FILENAME is None
    assert common.USER_ID is None
    assert common.INIT_FINISH is False
    return


def all_global_are_not_initial():
    """
    全てのグローバル変数が初期値とは別の値になっていることを確認する。
    """
    assert common.ROOT_DIR is not None
    assert common.USER_LIST_DIR is not None
    assert common.CURRENT_USER_FILE_DIR is not None
    assert common.CURRENT_USER_FILENAME is not None
    assert common.DB_DIR is not None
    assert common.DB_FILENAME is not None
    assert common.DB_BACKUP_FILENAME is not None
    assert common.FOODDATA_JSON_DIR is not None
    assert common.FOODDATA_JSON_FILENAME is not None
    assert common.USER_ID is not None
    assert common.INIT_FINISH is True
    return


def return_to_initial():
    """
    全てのグローバル変数を初期値に戻す（テスト用の関数）
    """
    common.ROOT_DIR = None
    common.USER_LIST_DIR = None
    common.CURRENT_USER_FILE_DIR = None
    common.CURRENT_USER_FILENAME = None
    common.DB_DIR = None
    common.DB_FILENAME = None
    common.DB_BACKUP_FILENAME = None
    common.FOODDATA_JSON_DIR = None
    common.FOODDATA_JSON_FILENAME = None
    common.USER_ID = None
    common.INIT_FINISH = False
    return


def test_init_01():
    """
    init関数をテストする。引数を空にする。
    """
    common.init()
    all_global_are_not_initial()
    assert common.USER_ID == common.USER_DEFAULT


def test_init_02():
    """
    init関数をテストする。引数(user_id)を何らか空ではなく、かつスペースを含まない値にする。
    """
    user_id = "this_user_is_test"
    common.init(user_id)
    all_global_are_not_initial()
    assert common.USER_ID == user_id


def test_init_03():
    """
    init関数をテストする。引数(user_id)を何らか空ではなく、かつスペースを含む値にする。
    """
    user_id = "this user is test"
    common.init(user_id)
    all_global_are_not_initial()

    user_id_expect = "this_user_is_test"
    assert common.USER_ID != user_id
    assert common.USER_ID == user_id_expect
