import streamlit as st
import pandas as pd
import io
import re
import math

# 1. Саҳифа созламалари
st.set_page_config(page_title="MEDEXTRA", layout="wide")

# 2. Логин функцияси (Оддий ва хатосиз)
def check_password():
    def password_entered():
        if st.session_state["password"] == "admin123" and st.session_state["user"] == "admin":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["user"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("🔐 MEDEXTRA Тизими")
        st.text_input("Логин", key="user")
        st.text_input("Парол", type="password", key="password")
        st.button("Кириш", on_click=password_entered)
        return False
    elif not st.session_state["password_correct"]:
        st.title("🔐 MEDEXTRA Тизими")
        st.text_input("Логин", key="user")
        st.text_input("Парол", type="password", key="password")
        st.button("Кириш", on_click=password_entered)
        st.error("❌ Логин ёки парол хато!")
        return False
    else:
        return True

# 3. Агар парол тўғри бўлса, асосий қисмни кўрсатиш
if check_password():
    st.sidebar.button("Тизимдан чиқиш", on_click=lambda: st.session_state.clear())
    st.title("💊 MEDEXTRA: Professional Hisob-Kitob")

    # Сизнинг идеал ишловчи формулангиз
    def get_pack_size(name):
        match = re.search(r'[N№](\d+)', str(name).upper())
        return int(match.group(1)) if match else 1

    def calculate_prices(cost, pack_size):
        # Пачка нархи: 12% устама ва 100 га яхлитлаш
        pachka_final = math.ceil((cost * 1.12) / 100) * 100
        # Дона нархи: пачка нархини бўлиб 100 га яхлитлаш
        dona_final = math.ceil((pachka_final / (pack_size if pack_size > 0 else 1)) / 100) * 100
        return pachka_final, dona_final

    uploaded_file = st.file_uploader("Excel (.xlsx) yuklang", type=['xlsx'])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        cols = df.columns.tolist()
        col_name = st.selectbox("Dori nomi (A):", cols, index=0)
        col_cost = st.selectbox("Tannarx (D):", cols, index=3 if len(cols)>3 else 0)
        
        if st.button("🚀 Hisoblash"):
            p_list, d_list = [], []
            for _, row in df.iterrows():
                try:
                    val = str(row[col_cost]).replace(' ', '').replace(',', '.')
                    cost = float(re.sub(r'[^\d.]', '', val))
                except: cost = 0
                
                size = get_pack_size(row[col_name])
                p_p, d_p = calculate_prices(cost, size)
                p_list.append(p_p)
                d_list.append(d_p)
            
            df['Pachka Sotuv (H)'] = p_list
            df['Dona Narxi (I)'] = d_list
            st.dataframe(df)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            st.download_button("📥 Yuklab olish", output.getvalue(), "medextra_tayyor.xlsx")
