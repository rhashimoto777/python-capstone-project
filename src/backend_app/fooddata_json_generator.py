import json
import os

from src.backend_app import backend_common as common


def generate_json():
    """
    初回起動時の処理。
    FoodDataテーブルの元となるjsonファイルを、./dataフォルダの直下に生成する。
    """
    common.init()
    _tentative_gen_json()  # TODO：正式な処理に書き換える
    return


def _tentative_gen_json():
    """
    本関数はあくまで骨組み確認用にダミーデータを作る用途であり、正式ファイルではない。
    本来はWebサイトをスクレイピングしてデータを取得してきたい。
    TODO : 正しい処理が実装されるタイミングで本関数を消すか改名すること。
    """
    id = "FoodDataID"
    name = "FoodName"
    kcal = "Calory_Total"
    Pg = "Grams_Protein"
    Fg = "Grams_Fat"
    Cg = "Grams_Carbo"
    SUn = "StandardUnit_Name"
    SUg = "StandardUnit_Grams"

    d = []
    d.append(
        {
            id: 0,
            name: "鶏もも肉(皮付き)",
            kcal: 190.0,
            Pg: 16.6,
            Fg: 14.2,
            Cg: 0.0,
            SUn: "100g",
            SUg: 100,
        }
    )
    d.append(
        {
            id: 1,
            name: "卵",
            kcal: 74.0,
            Pg: 6.34,
            Fg: 5.3,
            Cg: 0.21,
            SUn: "1個",
            SUg: 52,
        }
    )
    d.append(
        {
            id: 2,
            name: "玉ねぎ",
            kcal: 62.0,
            Pg: 1.88,
            Fg: 0.19,
            Cg: 15.79,
            SUn: "1個",
            SUg: 188,
        }
    )
    d.append(
        {
            id: 3,
            name: "米",
            kcal: 513.0,
            Pg: 9.15,
            Fg: 1.35,
            Cg: 116.4,
            SUn: "1合",
            SUg: 180,
        }
    )
    d.append(
        {
            id: 4,
            name: "サラダ油",
            kcal: 106.0,
            Pg: 0.0,
            Fg: 12.0,
            Cg: 0.0,
            SUn: "大さじ1",
            SUg: 12,
        }
    )
    d.append(
        {
            id: 5,
            name: "オリーブオイル",
            kcal: 107.0,
            Pg: 0.0,
            Fg: 12.0,
            Cg: 0.0,
            SUn: "大さじ1",
            SUg: 12,
        }
    )
    d.append(
        {
            id: 6,
            name: "醤油",
            kcal: 14.0,
            Pg: 1.39,
            Fg: 0.0,
            Cg: 1.42,
            SUn: "大さじ1",
            SUg: 18,
        }
    )
    d.append(
        {
            id: 7,
            name: "料理酒",
            kcal: 13.0,
            Pg: 0.03,
            Fg: 0.0,
            Cg: 0.71,
            SUn: "大さじ1",
            SUg: 15,
        }
    )
    d.append(
        {
            id: 8,
            name: "みりん",
            kcal: 43.0,
            Pg: 0.05,
            Fg: 0.0,
            Cg: 7.78,
            SUn: "大さじ1",
            SUg: 18,
        }
    )
    d.append(
        {
            id: 9,
            name: "にんにく",
            kcal: 6.6,
            Pg: 0.326,
            Fg: 0.046,
            Cg: 1.403,
            SUn: "1かけ",
            SUg: 5,
        }
    )
    d.append(
        {
            id: 10,
            name: "乾麺パスタ",
            kcal: 312.0,
            Pg: 11.61,
            Fg: 1.62,
            Cg: 65.79,
            SUn: "1食",
            SUg: 90,
        }
    )
    d.append(
        {
            id: 11,
            name: "いくら",
            kcal: 151.0,
            Pg: 19.56,
            Fg: 9.36,
            Cg: 0.12,
            SUn: "小鉢一杯",
            SUg: 60,
        }
    )

    os.chdir(common.FOODDATA_JSON_PATH)
    with open(common.FOODDATA_JSON_FILENAME, "w", encoding="utf-8") as file:
        json.dump(d, file, ensure_ascii=False, indent=4, sort_keys=True)
    return


if __name__ == "__main__":
    generate_json()