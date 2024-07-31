import streamlit as st
import pandas as pd

st.title('Test')
st.caption('This is the test apprication.')


ref_df = pd.read_json('refrigirator.json')
food_df = pd.read_json('fooddata.json')
view_df = pd.merge(ref_df, food_df, how='inner')


st.dataframe(view_df)