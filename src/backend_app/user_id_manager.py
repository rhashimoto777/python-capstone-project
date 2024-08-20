from src.backend_app import common_info as common
from pathlib import Path
import os


class UserIdManager:
    def __init__(self) -> None:
        common.init()  # 既に他の場所で呼ばれていれば何もしない
        self.user_id_list = None
        self.current_user = None
        self.__update()
        return

    def overwrite_current_user(self, user_id="user_default"):
        json_path = os.path.join(
            common.CURRENT_USER_FILE_DIR, common.CURRENT_USER_FILENAME
        )
        exist = Path(json_path).is_file()
        if exist:
            os.remove(json_path)

        with open(json_path, "w", encoding="utf-8") as file:
            file.write(user_id)

        self.__update()
        return

    def __update(self):
        # 一度Noneで初期化する
        self.user_id_list = None
        self.current_user = None

        # 値を詰め込む
        self.user_id_list = self.__get_user_id_list()
        self.current_user = self.__get_latest_user()
        return

    def __get_user_id_list():
        return [p.name for p in Path(common.USER_LIST_DIR).iterdir() if p.is_dir()]

    def __get_latest_user(self):
        json_path = os.path.join(
            common.CURRENT_USER_FILE_DIR, common.CURRENT_USER_FILENAME
        )
        exist = Path(json_path).is_file()
        if exist:
            with open(json_path, "r", encoding="utf-8") as file:
                userid = str(file.read())

                userid_list = self.user_id_list
                if userid_list is None:
                    userid_list = self.__get_user_id_list()

                if userid in self.__get_user_id_list():
                    return userid
        return "user_default"
