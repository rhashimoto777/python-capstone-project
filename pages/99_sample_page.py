from src import frontend_main
from src import translator
import streamlit as st


st.title("このページはマルチページの利用に関するサンプルページです")

#--------------------------------------------------------------------------------
st.subheader("【解説1】frontend_main.pyとの関係")
st.write('このファイル(99_sample_page.py)は、次のようなフォルダ関係にあります。')
code = '''
main.py
srcフォルダ
   - frontend_main.py
   - translator.py
pagesフォルダ
   - 99_sample_page.py
'''
st.code(code)
st.write("""
Streamlitの仕様上、実行ファイルであるmain.py、及びpagesフォルダ内の全ての.pyに対応するページが自動で生成されます。 \
そのため、仮にfrontend_main.pyがpagesフォルダ内にある場合、「frontend main」というページが作られてしまいます。
\n\n
一方で、pagesフォルダ内の各.pyで共通の関数を使いたいことが多々あると思われます。
そこで、基本的な表示処理はfrontend_main.pyに置き、pages内の.pyではfrontend.pyをimportして関数を呼び出すことで表示を使いまわせます。
""")

with st.form(key='sample_page_demo_call_frontend'):    
    st.text("fronend_main.py内の表示関数を呼び出す例")
    submit_btn1 = st.form_submit_button("「冷蔵庫の中にある食材の種類・数」を表示")
    submit_btn2 = st.form_submit_button("「登録済みの料理」を表示")
if submit_btn1:
    frontend_main.show_refrigerator_fooddata()
if submit_btn2:
    frontend_main.show_cookings_registered()
del submit_btn1, submit_btn2

#--------------------------------------------------------------------------------
st.subheader("【解説2】translator.pyとの関係")
st.write("""
pagesフォルダ内の個別.py内で特有の表示を行うときは。わざわざfrontend_main.pyに表示処理を書くよりも、pages内の.py内に表示処理を書いた方が簡便です。
\n\n
そういったときは、translator.pyをimportし、各種処理を行います。
""")

with st.form(key='sample_page_demo_call_translator'):    
    st.text("translator.py内の関数を呼び出して独自の表示を作る例")
    submit_btn = st.form_submit_button("「df_fooddata」を呼び出して表示")
if submit_btn:
    df_foodfata = translator.get_df_fooddata()
    st.table(df_foodfata)

#--------------------------------------------------------------------------------
st.subheader("【解説3】ページの表示順番")
st.markdown(
"""
- .pyのファイル名についている「99_」「01_」等の数字でページの表示順番を制御できます。
- このファイルも「99_sample_page.py」という名前ですが、Streamlitの表示上は「sample page」と表示されていると思います。
- 詳しくは **[この記事](https://qiita.com/nockn/items/f40a80cc79fcb358083c#%E3%83%9A%E3%83%BC%E3%82%B8%E3%81%AE%E9%A0%86%E7%95%AA%E3%82%92%E6%93%8D%E4%BD%9C%E3%81%99%E3%82%8B)**などを参照ください
"""
)


