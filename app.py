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
            font-size: 20px;
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
            font-size: 16px;
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
        [data-testid="stSidebar"] {{
            background-color: rgba(0, 74, 153, 0.95);
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

# 4. МАТЕМАТИК ФУНКЦИЯЛАР
def get_pack_size(name):
    name_upper = str(name).upper()
    if any(word in name_upper for word in ["САЛФЕТКА", "ЧОЙ", "CHAY", "SALFETKA", "МАРЛЯ", "БИНТ"]):
        return 1
    match = re.search(r'[N№](\d+)', name_upper)
    return int(match.group(1)) if match else 1

def admin_calculate(cost, pack_size):
    unit_cost = cost / pack_size
    safe_limit = unit_cost * 1.19
    res_unit = math.ceil((unit_cost * 1.14) / 1000) * 1000
    if res_unit > safe_limit: res_unit = math.ceil((unit_cost * 1.12) / 500) * 500
    if res_unit > safe_limit: res_unit = math.ceil((unit_cost * 1.10) / 100) * 100
    if res_unit > safe_limit: res_unit = math.floor(safe_limit / 100) * 100
    pachka_final = int(res_unit * pack_size)
    return pachka_final, int(res_unit)

def user_calculate(cost, pack_size, pct):
    pachka_raw = cost * (1 + pct / 100)
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
        login_u = st.text_input("Логин / Телефон")
        login_p = st.text_input("Парол", type="password")
        if st.button("КИРИШ"):
            users_df = load_users_data()
            entered_hash = hashlib.sha256(login_p.encode()).hexdigest()
            user_row = users_df[users_df['phone'].astype(str) == str(login_u)]
            if not user_row.empty:
                db_pass = str(user_row.iloc[0]['password'])
                if db_pass == entered_hash or db_pass == login_p:
                    if int(user_row.iloc[0]['status']) == 0:
                        st.warning("Админ тасдиқлашини кутинг!")
                    else:
                        st.session_state["auth"] = True
                        st.session_state["user"] = login_u
                        st.session_state["role"] = int(user_row.iloc[0]['status'])
                        st.rerun()
                else: st.error("Парол хато!")
            else: st.error("Фойдаланувчи топилмади!")
    
    with tab_reg:
        st.info("Рўйхатдан ўтиш учун админ билан боғланинг: +998 88 754 98 96")
    
    st.markdown('<div class="contact-box">📞 Боғланиш учун: +998 88 754 98 96</div>', unsafe_allow_html=True)
    st.stop()

# 6. MENU (SIDEBAR)
st.sidebar.title(f"👤 {st.session_state.get('user')}")
menu_options = ["🚀 Админ Ҳисоб-китоб", "📊 Фоизли Калькулятор"]
if st.session_state.get("role") == 9:
    menu_options.append("⚙️ Админ Панел")

menu = st.sidebar.radio("Бўлимни танланг:", menu_options)

# 7. BO'LIMLAR
if menu == "🚀 Админ Ҳисоб-китоб":
    st.markdown('<div class="blue-label">📋 АДМИН ҲИСОБЛАШ (14%-12%-10%)</div>', unsafe_allow_html=True)
    files = st.file_uploader("Excel/PDF танланг", accept_multiple_files=True)
    if files and st.button("🚀 ҲИСОБЛАШ"):
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w") as zf:
            for f in files:
                if f.name.endswith('xlsx'): df = pd.read_excel(f)
                else:
                    with pdfplumber.open(f) as p:
                        rows = []
                        for pg in p.pages:
                            if pg.extract_table(): rows.extend(pg.extract_table())
                        df = pd.DataFrame(rows[1:], columns=rows[0])
                
                p_l, d_l = [], []
                for _, row in df.iterrows():
                    try:
                        cost = float(re.sub(r'[^\d.]', '', str(row.iloc[3]).replace(',','.')))
                        p_f, d_f = admin_calculate(cost, get_pack_size(row.iloc[0]))
                        p_l.append(p_f); d_l.append(d_f)
                    except: p_l.append(0); d_l.append(0)
                df['Sotuv_Pachka'], df['Sotuv_Dona'] = p_l, d_l
                out = io.BytesIO()
                with pd.ExcelWriter(out, engine='xlsxwriter') as wr: df.to_excel(wr, index=False)
                zf.writestr(f"Admin_{f.name.replace('.pdf','.xlsx')}", out.getvalue())
        st.download_button("📥 ZIP ЮКЛАШ", zip_buf.getvalue(), "Admin_Natijalar.zip")

elif menu == "📊 Фоизли Калькулятор":
    st.markdown('<div class="blue-label">📊 ИХТИЁРИЙ ФОИЗЛИ ҲИСОБЛАШ</div>', unsafe_allow_html=True)
    user_pct = st.slider("Қўшиладиган фоизни танланг:", 1, 20, 10)
    u_files = st.file_uploader("Excel/PDF танланг", accept_multiple_files=True, key="u_up")
    if u_files and st.button("📊 ҲИСОБЛАШ"):
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w") as zf:
            for f in u_files:
                if f.name.endswith('xlsx'): df = pd.read_excel(f)
                else:
                    with pdfplumber.open(f) as p:
                        rows = []
                        for pg in p.pages:
                            if pg.extract_table(): rows.extend(pg.extract_table())
                        df = pd.DataFrame(rows[1:], columns=rows[0])
                
                p_l, d_l = [], []
                for _, row in df.iterrows():
                    try:
                        cost = float(re.sub(r'[^\d.]', '', str(row.iloc[3]).replace(',','.')))
                        p_f, d_f = user_calculate(cost, get_pack_size(row.iloc[0]), user_pct)
                        p_l.append(p_f); d_l.append(d_f)
                    except: p_l.append(0); d_l.append(0)
                df['Sotuv_Pachka'], df['Sotuv_Dona'] = p_l, d_l
                out = io.BytesIO()
                with pd.ExcelWriter(out, engine='xlsxwriter') as wr: df.to_excel(wr, index=False)
                zf.writestr(f"User_{user_pct}pct_{f.name.replace('.pdf','.xlsx')}", out.getvalue())
        st.download_button("📥 ZIP ЮКЛАШ", zip_buf.getvalue(), "User_Natijalar.zip")

elif menu == "⚙️ Админ Панел":
    st.markdown('<div class="blue-label">⚙️ ФОЙДАЛАНУВЧИЛАРНИ БОШҚАРИШ</div>', unsafe_allow_html=True)
    st.write("Google Sheets орқали янги фойдаланувчиларни тасдиқлашингиз мумкин.")
    st.info("Янги рўйхатдан ўтганларнинг 'status' устунини 0 дан 1 га ўзгартириб қўйинг.")
    st.link_button("🌐 Google Sheets-ни очиш", "https://docs.google.com/spreadsheets/d/1XyO5EqqDonEfQnmqr8j7SQNbVcx2SC93txhFVHoDGQA/edit")

st.markdown('<div class="contact-box">📞 Боғланиш учун: +998 88 754 98 96</div>', unsafe_allow_html=True)
