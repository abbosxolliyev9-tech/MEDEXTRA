import streamlit as st
import pandas as pd
import io
import re
import math
import pdfplumber
import sqlite3
import hashlib
import uuid
import zipfile

# 1. SAHIFA SOZLAMALARI
st.set_page_config(page_title="MEDEXTRA", page_icon="💊", layout="centered")

# 2. DATABASE (Faqat bir marta yaratiladi)
def init_db():
    conn = sqlite3.connect('medextra_users.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (phone TEXT PRIMARY KEY, password TEXT, name TEXT, session_id TEXT, status INTEGER)''')
    admin_pass = hashlib.sha256("Abbos96".encode()).hexdigest()
    c.execute('INSERT OR IGNORE INTO users VALUES (?,?,?,?,?)', 
              ('admin', admin_pass, 'ADMIN', '', 9))
    conn.commit()
    conn.close()

init_db()

# 3. DIZAYN (Sizga yoqqan ko'k uslub)
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
        .stButton>button {{
            background-color: #004a99 !important;
            color: white !important;
            width: 100%;
            font-weight: bold;
            border-radius: 8px;
            height: 45px;
            border: 1px solid white;
        }}
        .stTabs [data-baseweb="tab-list"] {{
            background-color: #004a99;
            border-radius: 8px;
            padding: 5px;
        }}
        .stTabs [data-baseweb="tab"] {{
            color: white !important;
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

# 5. LOGIN TIZIMI (KEY lar bilan to'g'rilandi)
if "auth" not in st.session_state: st.session_state["auth"] = False

if not st.session_state["auth"]:
    tab_log, tab_reg = st.tabs(["🔑 КИРИШ", "📝 РЎЙХАТДАН ЎТИШ"])
    
    with tab_log:
        st.markdown('<div class="blue-label">Тизимга кириш</div>', unsafe_allow_html=True)
        login_u = st.text_input("Логин / Телефон", key="login_user")
        login_p = st.text_input("Парол", type="password", key="login_pass")
        if st.button("КИРИШ", key="login_btn"):
            conn = sqlite3.connect('medextra_users.db')
            c = conn.cursor()
            hashed = hashlib.sha256(login_p.encode()).hexdigest()
            c.execute('SELECT * FROM users WHERE phone=? AND password=?', (login_u, hashed))
            user = c.fetchone()
            if user:
                if user[4] == 0: st.warning("Админ тасдиқлашини кутинг.")
                else:
                    st.session_state["auth"], st.session_state["user"], st.session_state["role"] = True, login_u, user[4]
                    st.rerun()
            else: st.error("Хато!")
            conn.close()

    with tab_reg:
        st.markdown('<div class="blue-label">Рўйхатдан ўтиш</div>', unsafe_allow_html=True)
        reg_name = st.text_input("Исмингиз", key="reg_name")
        reg_phone = st.text_input("Телефон", key="reg_phone")
        reg_pass = st.text_input("Парол ўйлаб топинг", type="password", key="reg_pass")
        if st.button("РЎЙХАТДАН ЎТИШ", key="reg_btn"):
            if reg_phone and reg_pass:
                conn = sqlite3.connect('medextra_users.db')
                c = conn.cursor()
                try:
                    hashed = hashlib.sha256(reg_pass.encode()).hexdigest()
                    c.execute('INSERT INTO users VALUES (?,?,?,?,?)', (reg_phone, hashed, reg_name, '', 0))
                    conn.commit()
                    st.success("Рўйхатдан ўтдингиз!")
                except: st.error("Бу рақам банд!")
                conn.close()
    st.stop()

# 6. ADMIN PANEL
if st.session_state.get("role") == 9:
    with st.expander("🛠 АДМИН ПАНЕЛИ"):
        conn = sqlite3.connect('medextra_users.db')
        c = conn.cursor()
        c.execute('SELECT phone, name FROM users WHERE status=0')
        for p_u in c.fetchall():
            if st.button(f"✅ Тасдиқлаш: {p_u[1]} ({p_u[0]})", key=p_u[0]):
                c.execute('UPDATE users SET status=1 WHERE phone=?', (p_u[0],))
                conn.commit()
                st.rerun()
        conn.close()

# 7. ASOSIY ISHCHI QISM (ZIP bilan)
st.markdown('<div class="blue-label">📋 ФАЙЛЛАРНИ ҲИСОБЛАШ</div>', unsafe_allow_html=True)
uploaded_files = st.file_uploader("Excel ёки PDF танланг", type=['xlsx', 'pdf'], accept_multiple_files=True)

if uploaded_files:
    try:
        # Ustunlarni aniqlash
        if uploaded_files[0].name.endswith('xlsx'):
            df_temp = pd.read_excel(uploaded_files[0])
        else:
            with pdfplumber.open(uploaded_files[0]) as p:
                df_temp = pd.DataFrame(p.pages[0].extract_table())
        cols = df_temp.columns.tolist()
        
        c1, c2 = st.columns(2)
        col_n = c1.selectbox("💊 Номи устуни", cols)
        col_c = c2.selectbox("💰 Таннарх устуни", cols, index=min(3, len(cols)-1))

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
    except Exception as e: st.error(f"Хато: {e}")
