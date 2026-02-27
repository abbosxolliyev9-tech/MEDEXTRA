import streamlit as st
import pandas as pd
import io
import re
import math
import streamlit_authenticator as stauth

st.set_page_config(page_title="MEDEXTRA", layout="wide")

# Фойдаланувчи маълумотлари
names = ['Administrator']
usernames = ['apteka']
passwords = ['+-456'] # Паролингиз

# Хавфсиз текширув тизимини созлаш
authenticator = stauth.Authenticate(
    {'usernames': {usernames[0]: {'name': names[0], 'password': passwords[0]}}},
    'medextra_cookie',
    'medextra_key',
    30
)

# Логин ойнаси
# Изоҳ: янги версияларда Hasher ишлатиш мажбурий эмас, оддий матнли парол ҳам бўлади
name, authentication_status, username = authenticator.login('Кириш', 'main')

if authentication_status == False:
    st.error('Логин ёки парол хато')
elif authentication_status == None:
    st.info('Тизимдан фойдаланиш учун логин ва паролни киритинг')
elif authentication_status:
    # --- ТИЗИМНИНГ ИЧКИ ҚИСМИ ---
    authenticator.logout('Чиқиш', 'sidebar')
    st.sidebar.success(f"Хуш келибсиз, {name}")
    
    st.title("💊 MEDEXTRA: Aqlli Narx Tizimi")

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
