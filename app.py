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
        background-attachment: fixed;
    }
    .main-block {
        background: rgba(0, 0, 0, 0.85);
        padding: 25px;
        border-radius: 15px;
        color: white;
        border: 1px solid #27AE60;
    }
    .stButton>button {
        background-color: #27AE60 !important;
        color: white !important;
        border-radius: 10px !important;
        height: 3em !important;
        width: 100% !important;
        font-weight: bold !important;
        border: none !important;
    }
    .stSelectbox label, .stSlider label, h1, h2, h3, p {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. МАНТИҚИЙ ФУНКЦИЯЛАР
def get_pack_size(name):
    match = re.search(r'[N№](\d+)', str(name).upper())
    return int(match.group(1)) if match else 1

def calculate_prices(cost, pack_size, markup_percent):
    if cost <= 0: return 0, 0
    # Фоиз қўшиш ва 50 сўмга тепага яхлитлаш
    pachka_raw = cost * (1 + markup_percent / 100)
    pachka_final = math.ceil(pachka_raw / 50) * 50
    # Дона нархи ва 50 сўмга тепага яхлитлаш
    dona_raw = pachka_final / pack_size
    dona_final = math.ceil(dona_raw / 100) * 100 # Донани 100 га яхлитлаш маъқулроқ
    return int(pachka_final), int(dona_final)

# 3. АСОСИЙ ҚИСМ
st.markdown('<div class="main-block">', unsafe_allow_html=True)
st.title("💊 MEDEXTRA: Aqlli Hisob-Kitob")

# Режим танлаш (Паролсиз, шунчаки танлов)
mode = st.radio("Ish rejimini tanlang:", ["👤 Mijoz (1-20%)", "🔐 Admin (300k qoidasi)"], horizontal=True)

if mode == "👤 Mijoz (1-20%)":
    user_markup = st.select_slider("Ustama foizini tanlang (%):", options=list(range(1, 21)), value=10)
else:
    st.info("Admin qoidasi: 300 000 dan past 10%, tepasi 8%. Yaxlitlash 50 so'm.")

# 4. ФАЙЛ ЮКЛАШ
uploaded_file = st.file_uploader("Excel faylni yuklang", type=['xlsx'])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    cols = df.columns.tolist()
    
    c1, c2 = st.columns(2)
    with c1: col_name = st.selectbox("Dori nomi ustuni (A):", cols, index=0)
    with c2: col_cost = st.selectbox("Tannarx ustuni (D):", cols, index=3 if len(cols)>3 else 0)
    
    if st.button("🚀 HISOBLASHNI BOSHLASH"):
        p_res, d_res = [], []
        
        for _, row in df.iterrows():
            try:
                v = str(row[col_cost]).replace(' ', '').replace(',', '.')
                cost = float(re.sub(r'[^\d.]', '', v))
            except: cost = 0
            
            size = get_pack_size(row[col_name])
            
            # Режимга қараб фоизни аниқлаш
            if mode == "🔐 Admin (300k qoidasi)":
                current_markup = 8 if cost >= 300000 else 10
            else:
                current_markup = user_markup
            
            p_val, d_val = calculate_prices(cost, size, current_markup)
            p_res.append(p_val)
            d_res.append(d_val)
            
        df['Pachka Sotuv (H)'] = p_res
        df['Dona Narxi (I)'] = d_res
        
        st.success(f"Natija tayyor! ({mode})")
        st.dataframe(df)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        st.download_button("📥 Faylni yuklab olish", output.getvalue(), "medextra_natija.xlsx")

st.markdown('</div>', unsafe_allow_html=True)
