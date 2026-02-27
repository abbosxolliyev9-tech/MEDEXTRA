import streamlit as st
import pandas as pd
import io
import re
import math
import streamlit_authenticator as stauth

st.set_page_config(page_title="MEDEXTRA", layout="wide")

# 1. Фойдаланувчи маълумотлари
# Парол бу сафар тўғридан-тўғри текшириладиган қилиб соддалаштирилди
names = ['Administrator']
usernames = ['admin']
passwords = ['admin123'] # Сизнинг паролингиз

# Паролларни хавфсиз форматга ўтказиш (янги усул)
hashed_passwords = stauth.Hasher(passwords).generate()

authenticator = stauth.Authenticate(
    {'usernames': {usernames[0]: {'name': names[0], 'password': hashed_passwords[0]}}},
    'medextra_cookie',
    'medextra_key',
    30
)

# 2. Логин ойнаси
name, authentication_status, username = authenticator.login('Кириш', 'main')

if authentication_status == False:
    st.error('Логин ёки парол хато')
elif authentication_status == None:
    st.warning('Илтимос, логин ва паролни киритинг')
elif authentication_status:
    # ТИЗИМ ИЧИДА
    authenticator.logout('Чиқиш', 'sidebar')
    st.sidebar.success(f"Хуш келибсиз, {name}")
    
    st.title("💊 MEDEXTRA: Professional Hisob-Kitob")

    # Сизнинг идеал ишловчи формулангиз
    def get_pack_size(name):
        match = re.search(r'[N№](\d+)', str(name).upper())
        return int(match.group(1)) if match else 1

    def calculate_prices(cost, pack_size):
        pachka_raw = cost * 1.12
        pachka_final = math.ceil(pachka_raw / 100) * 100
        dona_raw = pachka_final / (pack_size if pack_size > 0 else 1)
        dona_final = math.ceil(dona_raw / 100) * 100
        return pachka_final, dona_final

    uploaded_file = st.file_uploader("Excel faylni yuklang", type=['xlsx'])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        cols = df.columns.tolist()
        col_name = st.selectbox("Dori nomi (A):", cols, index=0)
        col_cost = st.selectbox("Tannarx (D):", cols, index=3 if len(cols)>3 else 0)
        
        if st.button("🚀 Hisoblashni boshlash"):
            pachka_list, dona_list = [], []
            for _, row in df.iterrows():
                try:
                    val = str(row[col_cost]).replace(' ', '').replace(',', '.')
                    cost = float(re.sub(r'[^\d.]', '', val))
                except: cost = 0
                
                size = get_pack_size(row[col_name])
                p_price, d_price = calculate_prices(cost, size)
                pachka_list.append(p_price)
                dona_list.append(d_price)
            
            df['Pachka Sotuv (H)'] = pachka_list
            df['Dona Narxi (I)'] = dona_list
            st.dataframe(df)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            st.download_button("📥 Faylni yuklab olish", output.getvalue(), "medextra_hisobot.xlsx")
