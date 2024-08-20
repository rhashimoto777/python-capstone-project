import os
from pathlib import Path

from src.backend_app import common_info as common


class UserIdManager:
    def __init__(self) -> None:
        common.init()  # 既に他の場所で呼ばれていれば何もしない
        self.user_id_list = None
        self.current_user = None
        self.__update()
        return

    def switch_user(self, user_id=common.USER_DEFAULT):
        fpath = os.path.join(common.CURRENT_USER_FILE_DIR, common.CURRENT_USER_FILENAME)
        # exist = Path(fpath).is_file()
        # if exist:
        #     os.remove(fpath)

        with open(fpath, "w", encoding="utf-8") as file:
            file.write(user_id)

        self.__update()
        return

    def __update(self):
        self.user_id_list = self.__get_user_id_list()
        self.current_user = self.__get_latest_user()
        return

    def __get_user_id_list(self):
        return [p.name for p in Path(common.USER_LIST_DIR).iterdir() if p.is_dir()]

    def __get_latest_user(self):
        fpath = os.path.join(common.CURRENT_USER_FILE_DIR, common.CURRENT_USER_FILENAME)
        exist = Path(fpath).is_file()
        if exist:
            with open(fpath, "r", encoding="utf-8") as file:
                userid = str(file.read())
                return userid
        return common.USER_DEFAULT
