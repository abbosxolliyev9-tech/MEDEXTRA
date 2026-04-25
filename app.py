import streamlit as st
import pandas as pd
import io
import re
import math

# 1. САҲИФА СОЗЛАМАЛАРИ ВА ДИЗАЙН (ФОН ВА ТУГМАЛАР)
st.set_page_config(page_title="MEDEXTRA", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1587854692152-cbe660feec90?q=80&w=2070");
        background-size: cover;
    }
    .main-block {
        background: rgba(0, 0, 0, 0.8);
        padding: 25px;
        border-radius: 15px;
        color: white;
    }
    .stButton>button {
        background-color: #27AE60;
        color: white;
        border-radius: 8px;
        height: 3em;
        width: 100%;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("💊 MEDEXTRA: Aqlli Hisob-Kitob")

# 2. МАНТИҚИЙ ФУНКЦИЯЛАР
def get_pack_size(name):
    match = re.search(r'[N№](\d+)', str(name).upper())
    return int(match.group(1)) if match else 1

def calculate_prices(cost, pack_size, markup_percent):
    if cost <= 0: return 0, 0
    # Фоизни қўллаш ва 50 сўмга тепага яхлитлаш
    pachka_raw = cost * (1 + markup_percent / 100)
    pachka_final = math.ceil(pachka_raw / 50) * 50
    # Дона нархи ва 50 сўмга тепага яхлитлаш
    dona_raw = pachka_final / pack_size
    dona_final = math.ceil(dona_raw / 50) * 50
    return int(pachka_final), int(dona_final)

# 3. РЕЖИМ ТАНЛАШ (SIDEBAR)
st.sidebar.header("⚙️ SOZLAMALAR")
mode = st.sidebar.radio("Ish rejimini tanlang:", ["👤 Mijoz (Erkin foiz)", "🔐 Admin (Maxsus qoida)"])

if mode == "👤 Mijoz (Erkin foiz)":
    st.subheader("👤 Mijozlar uchun hisob-kitob")
    user_markup = st.select_slider("Ustama фоизини танланг (%):", options=list(range(1, 21)), value=10)
else:
    st.subheader("🔐 Admin uchun maxsus қоида")
    st.info("Қоида: 300 000 дан пастга 10%, тепасига 8%. Яхлитлаш: 50 сўм.")

# 4. ФАЙЛ БИЛАН ИШЛАШ
uploaded_file = st.file_uploader("Excel (.xlsx) файлни юкланг", type=['xlsx'])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    cols = df.columns.tolist()
    
    col_name = st.selectbox("Dori nomi (A):", cols, index=0)
    col_cost = st.selectbox("Tannarx (D):", cols, index=3 if len(cols)>3 else 0)
    
    if st.button("🚀 ХИСОБЛАШНИ БОШЛАШ"):
        p_list, d_list = [], []
        
        for _, row in df.iterrows():
            try:
                val = str(row[col_cost]).replace(' ', '').replace(',', '.')
                cost = float(re.sub(r'[^\d.]', '', val))
            except: cost = 0
            
            size = get_pack_size(row[col_name])
            
            # Режимга қараб фоиз белгилаш
            if mode == "🔐 Admin (Maxsus qoida)":
                current_markup = 8 if cost >= 300000 else 10
            else:
                current_markup = user_markup
            
            p_val, d_val = calculate_prices(cost, size, current_markup)
            p_list.append(p_val)
            d_list.append(d_val)
            
        df['Pachka Sotuv (H)'] = p_list
        df['Dona Narxi (I)'] = d_list
        
        st.success(f"Natija tayyor! ({mode} rejimi)")
        st.dataframe(df)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        st.download_button("📥 Натижани юклаб олиш", output.getvalue(), "medextra_natija.xlsx")
