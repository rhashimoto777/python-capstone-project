import pandas as pd
import streamlit as st

from src import translator

st.set_page_config(layout="wide")

st.title("【冷蔵庫内の個数変更】")

col1, col2 = st.columns(2)

with col1:
    df_f = translator.get_df_fooddata()
    fid_list = df_f["FoodDataID"].tolist()

    df_r = translator.get_df_refrigerator()
    fidr_list = df_r["FoodDataID"].tolist()
    for fid in fid_list:
        if fid in fidr_list:
            continue
        else:
            new_row = pd.DataFrame([{"FoodDataID": fid, "Grams": 0.0}])
            df_r = pd.concat([df_r, new_row], ignore_index=True)

    df_r_edit = st.data_editor(df_r)
    df_r_edit = df_r_edit[df_r_edit["Grams"] > 0]

    button = st.button("変更反映", key="99_ref_edit")
    if button:
        translator.replace_refrigerator(df_r_edit)
with col2:
    df_f = translator.get_df_fooddata()
    df_f["標準単位の名称"] = df_f["StandardUnit_Name"]
    df_f["標準単位のグラム数"] = df_f["StandardUnit_Grams"]
    st.dataframe(
        df_f[["FoodDataID", "FoodName", "標準単位の名称", "標準単位のグラム数"]]
    )
