import streamlit as st
import pandas as pd
import io
import re
import math
import pdfplumber
import hashlib
import zipfile

# 1. SAHIFA SOZLAMALARI
st.set_page_config(page_title="MEDEXTRA", page_icon="💊", layout="centered")

# 2. DIZAYN
def add_custom_style():
    bg_image = "https://raw.githubusercontent.com/abbosxolliyev9-tech/MEDEXTRA/main/pexels-eren-34577902.jpg"
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("{bg_image}");
            background-size: cover;
            background-position: center;
        }}
        .blue-label {{
            background-color: #004a99;
            color: white !important;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
            font-size: 22px;
            margin-bottom: 20px;
            border: 1px solid white;
        }}
        /* Siz chizgan joy (Login tugmasi pasti) uchun stil */
        .contact-info {{
            background-color: rgba(0, 74, 153, 0.8);
            color: white;
            padding: 10px;
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
            margin-top: 20px;
            border: 1px solid white;
        }}
        .stButton>button {{
            background-color: #004a99 !important;
            color: white !important;
            width: 100%;
            font-weight: bold;
            border-radius: 8px;
            height: 45px;
            border: 1px solid white;
        }}
        </style>
        """, unsafe_allow_html=True)

add_custom_style()

# 3. GOOGLE SHEETS O'QISH (SODDA USUL)
# Linkni oxirini /export?format=csv qilib o'zgartirdik
SHEET_URL = "https://docs.google.com/spreadsheets/d/1XyO5EqqDonEfQnmqr8j7SQNbVcx2SC93txhFVHoDGQA/export?format=csv"

def load_users_data():
    try:
        return pd.read_csv(SHEET_URL)
    except:
        return pd.DataFrame(columns=['phone', 'password', 'name', 'status'])

# 4. MATEMATIK MANTIQ
def get_pack_size(name):
    match = re.search(r'[N№](\d+)', str(name).upper())
    return int(match.group(1)) if match else 1

def calculate_prices(cost, pack_size):
    pachka_raw = cost * 1.12
    pachka_final = math.ceil(pachka_raw / 100) * 100
    dona_raw = pachka_final / (pack_size if pack_size > 0 else 1)
    dona_final = math.ceil(dona_raw / 100) * 100
    return int(pachka_final), int(dona_final)

# 5. LOGIN TIZIMI
if "auth" not in st.session_state: st.session_state["auth"] = False

if not st.session_state["auth"]:
    tab_log, tab_reg = st.tabs(["🔑 КИРИШ", "📝 РЎЙХАТДАН ЎТИШ"])
    
    with tab_log:
        st.markdown('<div class="blue-label">Тизимга кириш</div>', unsafe_allow_html=True)
        login_u = st.text_input("Логин / Телефон", value="+998887549896")
        login_p = st.text_input("Парол", type="password")
        
        if st.button("КИРИШ"):
            users_df = load_users_data()
            hashed_p = hashlib.sha256(login_p.encode()).hexdigest()
            
            # Tekshirish
            check = users_df[(users_df['phone'].astype(str) == str(login_u)) & (users_df['password'] == hashed_p)]
            
            if not check.empty:
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("Login yoki parol xato!")
        
        # SIZ CHIZGAN JOYDA RAQAMNI CHIQARISH
        st.markdown('<div class="contact-info">📞 Боғланиш учун: +998 88 754 98 96</div>', unsafe_allow_html=True)

    with tab_reg:
        st.info("Ro'yxatdan o'tish uchun admin bilan bog'laning.")
        st.markdown('<div class="contact-info">📞 Админ: +998 88 754 98 96</div>', unsafe_allow_html=True)
    
    st.stop()

# 6. ISHCHI QISM (KIRGANDAN KEYIN)
st.markdown('<div class="blue-label">📋 ФАЙЛЛАРНИ ҲИСОБЛАШ</div>', unsafe_allow_html=True)
files = st.file_uploader("Excel yoki PDF yuklang", accept_multiple_files=True)

if files:
    if st.button("🚀 HISOB-KITOBNI BOSHLASH"):
        # Bu yerda fayllarni qayta ishlash kodi davom etadi...
        st.success("Fayllar qabul qilindi!")

st.markdown('<div class="contact-info">📞 Қўллаб-қувватlash: +998 88 754 98 96</div>', unsafe_allow_html=True)
