import streamlit as st
import pandas as pd
import io
import re
import math
import pdfplumber
import hashlib
import zipfile
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 1. SAHIFA SOZLAMALARI
st.set_page_config(page_title="MEDEXTRA", page_icon="💊", layout="centered")

# 2. GOOGLE SHEETS ULANISHI
SHEET_URL = "https://docs.google.com/spreadsheets/d/1XyO5EqqDonEfQnmqr8j7SQNbVcx2SC93txhFVHoDGQA/edit?usp=sharing"

def get_google_sheet():
    # Diqqat: Bu yerda ochiq havola orqali o'qish uchun pandas ishlatamiz
    csv_url = SHEET_URL.replace('/edit?usp=sharing', '/export?format=csv')
    return pd.read_csv(csv_url)

# 3. DIZAYN
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
        .footer {{
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: rgba(0, 74, 153, 0.8);
            color: white;
            text-align: center;
            padding: 10px;
            font-weight: bold;
            border-top: 1px solid white;
            z-index: 999;
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

# 4. MATEMATIK MANTIQ
def get_pack_size(name):
    name_upper = str(name).upper()
    if any(word in name_upper for word in ["САЛФЕТКА", "ЧОЙ", "CHAY", "SALFETKA", "МАРЛЯ", "БИНТ"]):
        return 1
    match = re.search(r'[N№](\d+)', name_upper)
    return int(match.group(1)) if match else 1

def calculate_prices(cost, pack_size):
    unit_cost = cost / pack_size
    safe_limit = unit_cost * 1.19
    res_unit = math.ceil((unit_cost * 1.14) / 1000) * 1000
    if res_unit > safe_limit: res_unit = math.ceil((unit_cost * 1.12) / 500) * 500
    if res_unit > safe_limit: res_unit = math.ceil((unit_cost * 1.10) / 100) * 100
    if res_unit > safe_limit: res_unit = math.floor(safe_limit / 100) * 100
    pachka_final = int(res_unit * pack_size)
    return pachka_final, int(res_unit), ((pachka_final / cost) - 1) * 100 if cost > 0 else 0

# 5. LOGIN TIZIMI
if "auth" not in st.session_state: st.session_state["auth"] = False

if not st.session_state["auth"]:
    tab_log, tab_reg = st.tabs(["🔑 КИРИШ", "📝 РЎЙХАТДАН ЎТИШ"])
    
    with tab_log:
        st.markdown('<div class="blue-label">Тизимга кириш</div>', unsafe_allow_html=True)
        login_u = st.text_input("Логин / Телефон", value="+998887549896", key="login_user")
        login_p = st.text_input("Парол", type="password", key="login_pass")
        
        if st.button("КИРИШ", key="login_btn"):
            try:
                users_df = get_google_sheet()
                hashed = hashlib.sha256(login_p.encode()).hexdigest()
                # Foydalanuvchini tekshirish
                user_row = users_df[(users_df['phone'].astype(str) == str(login_u)) & (users_df['password'] == hashed)]
                
                if not user_row.empty:
                    status = user_row.iloc[0]['status']
                    if status == 0:
                        st.warning("Админ тасдиқлашиni кутинг.")
                    else:
                        st.session_state["auth"] = True
                        st.session_state["user"] = login_u
                        st.session_state["role"] = status
                        st.rerun()
                else:
                    st.error("Raqam yoki parol xato!")
            except Exception as e:
                st.error(f"Ulanishda xato: {e}")

    with tab_reg:
        st.markdown('<div class="blue-label">Рўйхатдан ўтиш</div>', unsafe_allow_html=True)
        st.info("Ro'yxatdan o'tish uchun admin bilan bog'laning: +998887549896")
        st.write("Hozircha Google jadval orqali avtomatik yozish uchun maxsus API kalit kerak. Xavfsizlik uchun foydalanuvchilarni o'zingiz jadvalga qo'shib qo'yishingizni maslahat beraman.")
    
    st.markdown('<div class="footer">Боғланиш uchun: +998887549896</div>', unsafe_allow_html=True)
    st.stop()

# 6. ASOSIY ISHCHI QISM
st.markdown('<div class="blue-label">📋 ФАЙЛЛАРНИ ҲИСОБЛАШ</div>', unsafe_allow_html=True)
uploaded_files = st.file_uploader("Excel ёки PDF танланг", type=['xlsx', 'pdf'], accept_multiple_files=True)

if uploaded_files:
    try:
        if uploaded_files[0].name.endswith('xlsx'):
            df_temp = pd.read_excel(uploaded_files[0])
        else:
            with pdfplumber.open(uploaded_files[0]) as p:
                df_temp = pd.DataFrame(p.pages[0].extract_table())
        cols = df_temp.columns.tolist()
        
        c1, c2 = st.columns(2)
        col_n = c1.selectbox("💊 Номи устуни", cols)
        col_c = c2.selectbox("💰 Таннарх устуni", cols, index=min(3, len(cols)-1))

        if st.button("🚀 ҲИСОБЛАШ ВА ZIP ҚИЛИШ"):
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, "w") as zf:
                for f in uploaded_files:
                    if f.name.endswith('xlsx'): df = pd.read_excel(f)
                    else:
                        with pdfplumber.open(f) as p:
                            rows = []
                            for pg in p.pages:
                                if pg.extract_table(): rows.extend(pg.extract_table())
                            df = pd.DataFrame(rows[1:], columns=rows[0])
                    
                    df = df.fillna(0)
                    p_l, d_l, m_l = [], [], []
                    for _, row in df.iterrows():
                        try:
                            cost = float(re.sub(r'[^\d.]', '', str(row[col_c]).replace(',','.')))
                            p_p, d_d, m_m = calculate_prices(cost, get_pack_size(row[col_n]))
                            p_l.append(p_p); d_l.append(d_d); m_l.append(f"{m_m:.1f}%")
                        except: p_l.append(0); d_l.append(0); m_l.append("0%")
                    
                    df['Sotuv_Pachka'], df['Sotuv_Dona'], df['Ustama'] = p_l, d_l, m_l
                    out = io.BytesIO()
                    with pd.ExcelWriter(out, engine='xlsxwriter') as wr: df.to_excel(wr, index=False)
                    zf.writestr(f"Tayyor_{f.name.replace('.pdf','.xlsx')}", out.getvalue())
            
            st.download_button("📥 ZIP ЮКЛАШ", zip_buf.getvalue(), "Natijalar.zip")
    except Exception as e: st.error(f"Xato: {e}")

st.markdown('<div class="footer">Боғланиш uchun: +998887549896</div>', unsafe_allow_html=True)
