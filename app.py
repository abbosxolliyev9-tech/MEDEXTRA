import streamlit as st
import pandas as pd
import io
import re
import math
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- SAYT SOZLAMALARI ---
st.set_page_config(page_title="MEDEXTRA | Professional Tizim", layout="wide")

# Orqa fon va dizayn uchun CSS
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNKSIYALAR ---
def get_pack_size(name):
    match = re.search(r'[N№](\d+)', str(name).upper())
    return int(match.group(1)) if match else 1

def calculate_med_logic(cost, size):
    # Pachka narxi: 12% ustama va 100 ga tepaga yaxlitlash
    pachka_final = math.ceil((cost * 1.12) / 100) * 100
    # Dona narxi: Pachka / dona soni va 100 ga tepaga yaxlitlash
    dona_final = math.ceil((pachka_final / size) / 100) * 100
    return pachka_final, dona_final

# --- MENU STRUKTURASI ---
menu = ["Mijoz Hisob-kitob", "Admin Panel", "Google Sheets Ma'lumotlari"]
choice = st.sidebar.selectbox("Bo'limni tanlang", menu)

# --- 1. MIJOZ BO'LIMI ---
if choice == "Mijoz Hisob-kitob":
    st.title("💊 MEDEXTRA Mijozlar Bo'limi")
    st.write("Excel faylni yuklang va narxlarni avtomatik hisoblang.")
    
    uploaded_file = st.file_uploader("Faylni tanlang", type=['xlsx'])
    
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        cols = df.columns.tolist()
        
        c1, c2 = st.columns(2)
        with c1: col_name = st.selectbox("Dori nomi ustuni:", cols, index=0)
        with c2: col_cost = st.selectbox("Tannarx ustuni (D):", cols, index=3 if len(cols)>3 else 0)
        
        if st.button("🚀 HISOB-KITOBNI BOSHLASH"):
            p_list, d_list = [], []
            for _, row in df.iterrows():
                try:
                    val = str(row[col_cost]).replace(' ', '').replace(',', '.')
                    cost = float(re.sub(r'[^\d.]', '', val))
                except: cost = 0
                
                size = get_pack_size(row[col_name])
                p_price, d_price = calculate_med_logic(cost, size)
                p_list.append(p_price)
                d_list.append(d_price)
            
            df['Sotuv Narxi (Pachka)'] = p_list
            df['Sotuv Narxi (Dona)'] = d_list
            
            st.success("Hisoblash yakunlandi!")
            st.dataframe(df)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            st.download_button("📥 Natijani yuklab olish", output.getvalue(), "medextra_hisob.xlsx")

# --- 2. ADMIN PANEL ---
elif choice == "Admin Panel":
    st.title("🔐 Admin Boshqaruvi")
    password = st.text_input("Parolni kiriting", type="password")
    if password == "admin777": # Parolni o'zingizga moslang
        st.write("Tizim sozlamalari va statistikasi bu yerda ko'rinadi.")
        st.metric(label="Jami hisob-kitoblar", value="120")
    elif password:
        st.error("Parol noto'g'ri!")

# --- 3. GOOGLE SHEETS ---
elif choice == "Google Sheets Ma'lumotlari":
    st.title("📊 Google Sheets integratsiyasi")
    st.write("Bu bo'limda kelib tushgan so'rovlar ko'rinadi.")
    # Google Sheets ulanishi uchun json fayl va sozlamalar kerak
    st.info("Google Sheets ma'lumotlarini ko'rish uchun creds.json sozlanishi kerak.")
    # (Bu yerga Google Sheets ulanish kodlarini qo'shishingiz mumkin)
