import json
import os
import common

def init():
    """
    初回起動時の処理。
    FoodDataテーブルの元となるjsonファイルを、./dataフォルダの直下に生成する。
    """
    # 本当はWebサイトをスクレイピングなどできると理想的だが、暫定的にダミーデータを入れる。
    _tentative_gen_json() # TODO：正式な処理に書き換える
    return

def _tentative_gen_json():
    """
    本関数はあくまで骨組み確認用にダミーデータを作る用途であり、正式ファイルではない。
    TODO : 正しい処理が実装されるタイミングで本関数を消すか改名すること。
    """
    name = "FoodName"
    kcal = "Calory_Total"
    Pg =  "Grams_Protein"
    Fg = "Grams_Fat"
    Cg = "Grams_Carbo"
    SUn = "StandardUnit_Name"
    SUg = "StandardUnit_Grams"


    d = []
    d.append({name:"鶏もも肉(皮付き)", kcal:190.0, Pg:16.6, Fg:14.2, Cg:0.0, SUn:"100g", SUg:100})
    d.append({name:"卵", kcal:74.0, Pg:6.34, Fg:5.3, Cg:0.21, SUn:"1個", SUg:52})
    d.append({name:"玉ねぎ", kcal:62.0, Pg:1.88, Fg:0.19, Cg:15.79, SUn:"1個", SUg:188})
    d.append({name:"米", kcal:513.0, Pg:9.15, Fg:1.35, Cg:116.4, SUn:"1合", SUg:180})
    d.append({name:"サラダ油", kcal:106.0, Pg:0.0, Fg:12.0, Cg:0.0, SUn:"大さじ1", SUg:12})
    d.append({name:"オリーブオイル", kcal:107.0, Pg:0.0, Fg:12.0, Cg:0.0, SUn:"大さじ1", SUg:12})
    d.append({name:"醤油", kcal:14.0, Pg:1.39, Fg:0.0, Cg:1.42, SUn:"大さじ1", SUg:18})
    d.append({name:"料理酒", kcal:13.0, Pg:0.03, Fg:0.0, Cg:0.71, SUn:"大さじ1", SUg:15})
    d.append({name:"みりん", kcal:43.0, Pg:0.05, Fg:0.0, Cg:7.78, SUn:"大さじ1", SUg:18})
    d.append({name:"にんにく", kcal:6.6, Pg:0.326, Fg:0.046, Cg:1.403, SUn:"1かけ", SUg:5})
    d.append({name:"乾麺パスタ", kcal:312.0, Pg:11.61, Fg:1.62, Cg:65.79, SUn:"1食", SUg:90})
    d.append({name:"いくら", kcal:151.0, Pg:19.56, Fg:9.36, Cg:0.12, SUn:"小鉢一杯", SUg:60})

    os.chdir(common.FOODDATA_JSON_PATH)
    with open(common.FOODDATA_JSON_FILENAME, 'w', encoding='utf-8') as file:
        json.dump(d, file, ensure_ascii=False, indent=4, sort_keys=True)
    