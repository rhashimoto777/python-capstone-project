import pytest
from src.backend_app import user_id_manager as uim


@pytest.fixture(autouse=True)
def setup_and_teardown():
    uim_instance = uim.UserIdManager()
    current_user = uim_instance.current_user

    yield uim_instance

    uim_instance.overwrite_current_user(current_user)
    return


def test_init(setup_and_teardown):
    user_id_mananger = setup_and_teardown
    assert len(user_id_mananger.user_id_list) >= 2
    assert "user_default" in user_id_mananger.user_id_list
    assert "_PYTEST_" in user_id_mananger.user_id_list
    return


def test_overwrite_current_user(setup_and_teardown):
    user_id_mananger = setup_and_teardown
    sample_id = "sample_test_for_ocu"
    assert sample_id not in user_id_mananger.user_id_list

    user_id_mananger.overwrite_current_user(sample_id)
    assert sample_id == user_id_mananger.current_user
    return
