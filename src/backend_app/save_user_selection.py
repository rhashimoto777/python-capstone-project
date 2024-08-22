import json
import os
from pathlib import Path

from src.backend_app import common_info as common

JSON_DEFAULT_NAME = "user_temporal_selection"


def save(key: str, data):
    json_path = __gen_json_full_path(key)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4, sort_keys=True)
    return


def restore(key: str):
    json_path = __gen_json_full_path(key)
    exist = Path(json_path).is_file()

    if exist:
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data
    return None


def __gen_json_full_path(key: str):
    global JSON_DEFAULT_NAME
    json_full_name = f"{JSON_DEFAULT_NAME}_{key}.json"
    return os.path.join(common.DB_DIR, json_full_name)
