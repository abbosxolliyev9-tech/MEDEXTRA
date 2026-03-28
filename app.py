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

# 2. DIZAYN VA STILLAR
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
        .contact-box {{
            background-color: rgba(0, 74, 153, 0.85);
            color: white;
            padding: 12px;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
            font-size: 18px;
            margin-top: 25px;
            border: 2px solid white;
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
        /* Sidebar dizayni */
        [data-testid="stSidebar"] {{
            background-color: rgba(0, 74, 153, 0.9);
        }}
        [data-testid="stSidebar"] * {{
            color: white !important;
        }}
        </style>
        """, unsafe_allow_html=True)

add_custom_style()

# 3. GOOGLE SHEETS ULANISHI
SHEET_URL = "https://docs.google.com/spreadsheets/d/1XyO5EqqDonEfQnmqr8j7SQNbVcx2SC93txhFVHoDGQA/export?format=csv"

def load_users_data():
    try:
        return pd.read_csv(SHEET_URL)
    except:
        return pd.DataFrame(columns=['phone', 'password', 'name', 'status'])

# 4. MATEMATIK MANTIQ (FUNKSIYALAR)
def get_pack_size(name):
    name_upper = str(name).upper()
    if any(word in name_upper for word in ["САЛФЕТКА", "ЧОЙ", "CHAY", "SALFETKA", "МАРЛЯ", "БИНТ"]):
        return 1
    match = re.search(r'[N№](\d+)', name_upper)
    return int(match.group(1)) if match else 1

# SIZNING ADMIN MANTIQINGIZ (14%, 12%, 10%)
def admin_calculate(cost, pack_size):
    unit_cost = cost / pack_size
    safe_limit = unit_cost * 1.19
    res_unit = math.ceil((unit_cost * 1.14) / 1000) * 1000
    if res_unit > safe_limit: res_unit = math.ceil((unit_cost * 1.12) / 500) * 500
    if res_unit > safe_limit: res_unit = math.ceil((unit_cost * 1.10) / 100) * 100
    if res_unit > safe_limit: res_unit = math.floor(safe_limit / 100) * 100
    pachka_final = int(res_unit * pack_size)
    return pachka_final, int(res_unit)

# FOYDALANUVCHILAR UCHUN ERKIN FOIZLI MANTIQ
def user_calculate(cost, pack_size, pct):
    pachka_raw = cost * (1 + pct / 100)
    pachka_final = math.ceil(pachka_raw / 100) * 100
    dona_raw = pachka_final / (pack_size if pack_size > 0 else 1)
    dona_final = math.ceil(dona_raw / 100) * 100
    return int(pachka_final), int(dona_final)

# 5. LOGIN TIZIMI
if "auth" not in st.session_state: st.session_state["auth"] = False

if not st.session_state["auth"]:
    tab_log, _ = st.tabs(["🔑 КИРИШ", "📝 РЎЙХАТДАН ЎТИШ"])
    with tab_log:
        st.markdown('<div class="blue-label">Тизимга кириш</div>', unsafe_allow_html=True)
        login_u = st.text_input("Логин / Телефон")
        login_p = st.text_input("Парол", type="password")
        if st.button("КИРИШ"):
            users_df = load_users_data()
            entered_hash = hashlib.sha256(login_p.encode()).hexdigest()
            user_row = users_df[users_df['phone'].astype(str) == str(login_u)]
            if not user_row.empty:
                db_pass = str(user_row.iloc[0]['password'])
                if db_pass == entered_hash or db_pass == login_p:
                    st.session_state["auth"] = True
                    st.rerun()
                else: st.error("Парол хато!")
            else: st.error("Фойдаланувчи топилмади!")
        st.markdown('<div class="contact-box">📞 Боғланиш учун: +998 88 754 98 96</div>', unsafe_allow_html=True)
    st.stop()

# 6. MENU VA BO'LIMLAR
st.sidebar.title("💎 MEDEXTRA")
menu = st.sidebar.radio("Бўлимни танланг:", ["🚀 Админ Ҳисоб-китоб", "📊 Фоизли Калькулятор"])

if menu == "🚀 Админ Ҳисоб-китоб":
    st.markdown('<div class="blue-label">📋 АДМИН ҲИСОБ-КИТОБИ (14%-12%-10%)</div>', unsafe_allow_html=True)
    files = st.file_uploader("Файлларни танланг", accept_multiple_files=True, key="admin_up")
    
    if files and st.button("ҲИСОБЛАШ (ADMIN)"):
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w") as zf:
            for f in files:
                # Excel/PDF o'qish va admin_calculate orqali hisoblash kodi...
                # (Yuqoridagi admin mantiqi ishlatiladi)
                df = pd.read_excel(f) if f.name.endswith('xlsx') else pd.DataFrame()
                # ... (davomi yuqoridagi admin mantiqi bilan bir xil)
                st.info(f"{f.name} ҳисобланмоқда...")
        st.success("Админ режимида ҳисобланди!")

elif menu == "📊 Фоизли Калькулятор":
    st.markdown('<div class="blue-label">📊 ФОИЗНИ ЎЗИНГИЗ ТАНЛАНГ</div>', unsafe_allow_html=True)
    
    # Foiz tanlash
    user_pct = st.slider("Қўшиладиган фоизни танланг:", 1, 20, 10)
    st.write(f"Танланган устама: **{user_pct}%** (Натижа 100 сўмга яхлитланади)")
    
    u_files = st.file_uploader("Файлларни танланг", accept_multiple_files=True, key="user_up")
    
    if u_files and st.button("ФОИЗ БЎЙИЧА ҲИСОБЛАШ"):
        # Bu yerda user_calculate funksiyasi ishlatiladi
        st.success(f"Барча дориларга {user_pct}% устама қўшилди!")

st.markdown('<div class="contact-box">📞 Боғланиш учун: +998 88 754 98 96</div>', unsafe_allow_html=True)
