import streamlit as st
import pandas as pd
import io
import re
import math
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# 1. Саҳифа созламалари
st.set_page_config(page_title="MEDEXTRA | Тизимга кириш", layout="wide")

# 2. Фойдаланувчилар маълумотлар базаси (Вақтинчалик шу ерда)
# Паролни "хеш"ланган ҳолатда сақлаш хавфсизроқ
# Бу ерда: логин - admin, парол - admin123
config = {
    'credentials': {
        'usernames': {
            'admin': {
                'name': 'Administrator',
                'password': 'abc', # Бу ерда 'abc' хешланади
                'email': 'admin@medextra.uz'
            }
        }
    },
    'cookie': {
        'expiry_days': 30,
        'key': 'some_signature_key',
        'name': 'some_cookie_name'
    }
}

# Паролни хавфсиз қилиш (Сизнинг паролингиз: admin123)
# Бу қисм паролни код ичида очиқ кўринмаслиги учун керак
hashed_passwords = stauth.Hasher(['admin123']).generate()
config['credentials']['usernames']['admin']['password'] = hashed_passwords[0]

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# 3. Логин ойнасини чиқариш
name, authentication_status, username = authenticator.login('Кириш', 'main')

if authentication_status == False:
    st.error('Логин ёки парол хато')
elif authentication_status == None:
    st.warning('Илтимос, логин ва паролни киритинг')
elif authentication_status:
    # --- ТИЗИМ ИЧИДА ---
    authenticator.logout('Чиқиш', 'sidebar')
    st.sidebar.title(f"Хуш келибсиз, {name}")
    
    st.title("💊 MEDEXTRA: Professional Hisob-Kitob")

    def get_pack_size(name):
        match = re.search(r'[N№](\d+)', str(name).upper())
        return int(match.group(1)) if match else 1

    def calculate_prices(cost, pack_size):
        pachka_raw = cost * 1.12
        pachka_final = math.ceil(pachka_raw / 100) * 100
        dona_raw = pachka_final / pack_size
        dona_final = math.ceil(dona_raw / 100) * 100
        return pachka_final, dona_final

    uploaded_file = st.file_uploader("Excel faylni yuklang", type=['xlsx'])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        cols = df.columns.tolist()
        col_name = st.selectbox("Dori nomi (A):", cols, index=0)
        col_cost = st.selectbox("Tannarx (D):", cols, index=3 if len(cols)>3 else 0)
        
        if st.button("🚀 Formulani ishga tushirish"):
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
