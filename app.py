import streamlit as st
import pandas as pd
import io
import re
import math
import hashlib
import zipfile
# 1. Ҳисоб-китоб блоки
from calculations.logic import admin_calculate, user_calculate, get_pack_size
# 2. ТИЗИМ (Кириш/Чиқиш) блоки - Янги папкадан чақириш
from тизим.кириш import сессияни_тайёрлаш, чиқиш_тугмаси, кириш_ойнаси

# --- САҲИФА СОЗЛАМАЛАРИ ---
st.set_page_config(page_title="MEDEXTRA", page_icon="💊", layout="centered")

# --- ДИЗАЙН ---
def add_custom_style():
    bg_image = "https://raw.githubusercontent.com/abbosxolliyev9-tech/MEDEXTRA/main/pexels-eren-34577902.jpg"
    st.markdown(f"""
        <style>
        .stApp {{ background-image: url("{bg_image}"); background-size: cover; background-position: center; }}
        .blue-label {{ background-color: #004a99; color: white !important; padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 20px; margin-bottom: 20px; border: 1px solid white; }}
        .contact-box {{ background-color: rgba(0, 74, 153, 0.85); color: white; padding: 12px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 16px; margin-top: 25px; border: 2px solid white; }}
        .stButton>button {{ background-color: #004a99 !important; color: white !important; width: 100%; font-weight: bold; border-radius: 8px; height: 45px; border: 1px solid white; }}
        [data-testid="stSidebar"] {{ background-color: rgba(0, 74, 153, 0.95); }}
        [data-testid="stSidebar"] * {{ color: white !important; }}
        </style>
        """, unsafe_allow_html=True)

add_custom_style()

# --- ТИЗИМНИ ИШГА ТУШИРИШ ---
сессияни_тайёрлаш()

# Агар фойдаланувчи кирмаган бўлса, кириш ойнасини кўрсатиш ва тўхтатиш
if not st.session_state.get("auth"):
    кириш_ойнаси()
    st.markdown('<div class="contact-box">📞 Боғланиш: +998 88 754 98 96</div>', unsafe_allow_html=True)
    st.stop()

# Агар кирган бўлса, Sidebar-да чиқиш тугмасини чиқариш
чиқиш_тугмаси()

# --- GOOGLE SHEETS ВА МЕНЮ ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1XyO5EqqDonEfQnmqr8j7SQNbVcx2SC93txhFVHoDGQA/export?format=csv"

st.sidebar.title("💎 MEDEXTRA")
# Рольни текшириш (Админ ёки Оддий фойдаланувчи)
role = st.session_state.get("user")
menu_options = ["🚀 Админ Ҳисоб", "📊 Фоизли Кальк", "⚙️ Панел"] if role == "Администратор" else ["📊 Фоизли Кальк"]
menu = st.sidebar.radio("Бўлим:", menu_options)

# --- ИШЧИ ҚИСМЛАР ---
if menu in ["🚀 Админ Ҳисоб", "📊 Фоизли Кальк"]:
    title = "АДМИН ҲИСОБЛАШ (14-12-10%)" if menu == "🚀 Админ Ҳисоб" else "ИХТИЁРИЙ ФОИЗЛИ ҲИСОБЛАШ"
    st.markdown(f'<div class="blue-label">{title}</div>', unsafe_allow_html=True)
    
    if menu == "📊 Фоизли Кальк":
        user_pct = st.slider("Устама фоизини танланг:", 1, 25, 12)
    
    uploaded_files = st.file_uploader("Excel файлларни юкланг", type=['xlsx'], accept_multiple_files=True)
    
    if uploaded_files:
        sample_df = pd.read_excel(uploaded_files[0])
        cols = sample_df.columns.tolist()
        
        c1, c2 = st.columns(2)
        col_n = c1.selectbox("💊 Номи устуни (A):", cols, index=0)
        col_c = c2.selectbox("💰 Таннарх устуни (E):", cols, index=min(4, len(cols)-1))
        
        if st.button("🚀 ҲАММАСИНИ ҲИСОБЛАШ ВА ZIP ҚИЛИШ"):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for f in uploaded_files:
                    try:
                        df = pd.read_excel(f)
                        p_l, d_l = [], []
                        for _, row in df.iterrows():
                            try:
                                cost = float(re.sub(r'[^\d.]', '', str(row[col_c]).replace(',','.')))
                                pack = get_pack_size(row[col_n])
                                if menu == "🚀 Админ Ҳисоб": p_f, d_f = admin_calculate(cost, pack)
                                else: p_f, d_f = user_calculate(cost, pack, user_pct)
                                p_l.append(p_f); d_l.append(d_f)
                            except: p_l.append(0); d_l.append(0)
                        
                        df['Sotuv_Pachka'], df['Sotuv_Dona'] = p_l, d_l
                        excel_out = io.BytesIO()
                        with pd.ExcelWriter(excel_out, engine='xlsxwriter') as wr:
                            df.to_excel(wr, index=False)
                        zf.writestr(f"Tayyor_{f.name}", excel_out.getvalue())
                    except Exception as e:
                        st.error(f"Хатолик: {f.name} - {e}")
            
            st.success(f"✅ {len(uploaded_files)} та файл ҳисобланди!")
            st.download_button(label="📥 ZIP ЮКЛАШ", data=zip_buffer.getvalue(), file_name="Natijalar.zip", mime="application/zip")

elif menu == "⚙️ Панел":
    st.markdown('<div class="blue-label">⚙️ БОШҚАРУВ</div>', unsafe_allow_html=True)
    st.link_button("🌐 Google Sheets-ни очиш", SHEET_URL.replace('/export?format=csv', '/edit'))

st.markdown('<div class="contact-box">📞 Боғланиш учун: +998 88 754 98 96</div>', unsafe_allow_html=True)
