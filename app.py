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

# 1. САҲИФА СОЗЛАМАЛАРИ
st.set_page_config(page_title="MEDEXTRA", page_icon="💊", layout="centered")

# 2. DATABASE СОЗЛАМАЛАРИ
def init_db():
    conn = sqlite3.connect('medextra_users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (phone TEXT PRIMARY KEY, password TEXT, name TEXT, session_id TEXT, status INTEGER)''')
    admin_pass = hashlib.sha256("Abbos96".encode()).hexdigest()
    c.execute('INSERT OR IGNORE INTO users VALUES (?,?,?,?,?)', 
              ('admin', admin_pass, 'ADMIN', '', 9))
    conn.commit()
    conn.close()

init_db()

# 3. ДИЗАЙН (Сизга ёққан кўк услуб)
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
            text-shadow: 1px 1px 2px black;
        }}
        .stButton>button {{
            background-color: #004a99 !important;
            color: white !important;
            width: 100%;
            font-weight: bold;
            border-radius: 8px;
            height: 50px;
            border: 2px solid white;
        }}
        .stSelectbox label, .stFileUploader label, .stTabs [data-baseweb="tab-list"] {{
            background-color: rgba(0, 74, 153, 0.9) !important;
            color: white !important;
            border-radius: 5px;
            padding: 5px 10px;
        }}
        .footer-box {{
            background-color: #004a99;
            color: white;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            margin-top: 20px;
        }}
        </style>
        """, unsafe_allow_html=True)

add_custom_style()

# 4. МАТЕМАТИК МАНТИҚ
def get_pack_size(name):
    name_upper = str(name).upper()
    not_for_pieces = ["САЛФЕТКА", "ЧОЙ", "CHAY", "SALFETKA", "МАРЛЯ", "БИНТ"]
    if any(word in name_upper for word in not_for_pieces):
        return 1
    match = re.search(r'[N№](\d+)', name_upper)
    return int(match.group(1)) if match else 1

def calculate_prices(cost, pack_size):
    unit_cost = cost / pack_size
    safe_limit = unit_cost * 1.19  # 19% хавфсиз чегара
    
    # Яхлитлаш мантиғи: 1000 -> 500 -> 100
    res_unit = math.ceil((unit_cost * 1.14) / 1000) * 1000
    if res_unit > safe_limit:
        res_unit = math.ceil((unit_cost * 1.12) / 500) * 500
    if res_unit > safe_limit:
        res_unit = math.ceil((unit_cost * 1.10) / 100) * 100
    if res_unit > safe_limit:
        res_unit = math.floor(safe_limit / 100) * 100

    pachka_final = int(res_unit * pack_size)
    dona_final = int(res_unit)
    real_markup = ((pachka_final / cost) - 1) * 100 if cost > 0 else 0
    return pachka_final, dona_final, real_markup

# 5. КИРИШ / РЎЙХАТДАН ЎТИШ
if "auth" not in st.session_state: st.session_state["auth"] = False

if not st.session_state["auth"]:
    tab_log, tab_reg = st.tabs(["🔑 КИРИШ", "📝 РЎЙХАТДАН ЎТИШ"])
    
    with tab_log:
        st.markdown('<div class="blue-label">Тизимга кириш</div>', unsafe_allow_html=True)
        login_u = st.text_input("Телефон (ёки admin)")
        login_p = st.text_input("Парол", type="password")
        if st.button("КИРИШ", key="login_btn"):
            conn = sqlite3.connect('medextra_users.db')
            c = conn.cursor()
            hashed = hashlib.sha256(login_p.encode()).hexdigest()
            c.execute('SELECT * FROM users WHERE phone=? AND password=?', (login_u, hashed))
            user = c.fetchone()
            if user:
                if user[4] == 0:
                    st.warning("Ҳисобингиз ҳали фаоллаштирилмаган.")
                else:
                    new_sid = str(uuid.uuid4())
                    c.execute('UPDATE users SET session_id=? WHERE phone=?', (new_sid, login_u))
                    conn.commit()
                    st.session_state["auth"], st.session_state["user"], st.session_state["sid"], st.session_state["role"] = True, login_u, new_sid, user[4]
                    st.rerun()
            else: st.error("Маълумотлар хато!")
            conn.close()

    with tab_reg:
        st.markdown('<div class="blue-label">Янги фойдаланувчи</div>', unsafe_allow_html=True)
        reg_name = st.text_input("Исмингиз")
        reg_phone = st.text_input("Телефон")
        reg_pass = st.text_input("Парол", type="password")
        if st.button("РЎЙХАТДАН ЎТИШ"):
            if reg_phone and reg_pass:
                conn = sqlite3.connect('medextra_users.db')
                c = conn.cursor()
                try:
                    hashed = hashlib.sha256(reg_pass.encode()).hexdigest()
                    c.execute('INSERT INTO users VALUES (?,?,?,?,?)', (reg_phone, hashed, reg_name, '', 0))
                    conn.commit()
                    st.success("Рўйхатдан ўтдингиз! Админ тасдиқлашини кутинг.")
                except: st.error("Бу рақам банд!")
                conn.close()
    st.stop()

# 6. АДМИН ПАНЕЛ
if st.session_state.get("role") == 9:
    with st.expander("🛠 АДМИН ПАНЕЛИ"):
        conn = sqlite3.connect('medextra_users.db')
        c = conn.cursor()
        c.execute('SELECT phone, name FROM users WHERE status=0')
        pending = c.fetchall()
        for p_user in pending:
            col_u, col_b = st.columns([3, 1])
            col_u.write(f"👤 {p_user[1]} ({p_user[0]})")
            if col_b.button("✅ Тасдиқлаш", key=p_user[0]):
                c.execute('UPDATE users SET status=1 WHERE phone=?', (p_user[0],))
                conn.commit()
                st.rerun()
        conn.close()

# 7. АСОСИЙ ИШЧИ ҚИСМ
st.markdown('<div class="blue-label">📋 ФАЙЛЛАРНИ ҲИСОБЛАШ</div>', unsafe_allow_html=True)

uploaded_files = st.file_uploader("Excel ёки PDF файлларни танланг", type=['xlsx', 'pdf'], accept_multiple_files=True)

if uploaded_files:
    # Устунларни аниқлаш учун биринчи файлни ўқиймиз
    try:
        if uploaded_files[0].name.endswith('xlsx'):
            df_cols = pd.read_excel(uploaded_files[0])
        else:
            with pdfplumber.open(uploaded_files[0]) as p:
                df_cols = pd.DataFrame(p.pages[0].extract_table())
        cols = df_cols.columns.tolist()
    except:
        cols = ["Устун танланг"]

    c1, c2 = st.columns(2)
    col_n = c1.selectbox("💊 Дори номи устуни", cols)
    col_c = c2.selectbox("💰 Таннарх устуни", cols, index=min(3, len(cols)-1))

    if st.button("🚀 БАРЧАСИНИ ҲИСОБЛАШ ВА ZIP ҚИЛИШ"):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            for f in uploaded_files:
                try:
                    if f.name.endswith('xlsx'):
                        df = pd.read_excel(f)
                    else:
                        all_t = []
                        with pdfplumber.open(f) as p:
                            for pg in p.pages:
                                tbl = pg.extract_table()
                                if tbl: all_t.extend(tbl)
                        df = pd.DataFrame(all_t[1:], columns=all_t[0])
                    
                    df = df.fillna(0)
                    p_l, d_l, m_l = [], [], []
                    for _, row in df.iterrows():
                        try:
                            name = str(row[col_n])
                            cost = float(re.sub(r'[^\d.]', '', str(row[col_c]).replace(' ', '').replace(',', '.')))
                            size = get_pack_size(name)
                            pp, dd, mm = calculate_prices(cost, size)
                            p_l.append(pp); d_l.append(dd); m_l.append(f"{mm:.2f}%")
                        except: p_l.append(0); d_l.append(0); m_l.append("0%")
                    
                    df['Sotuv_Pachka'], df['Sotuv_Dona'], df['Наценка'] = p_l, d_l, m_l
                    
                    out = io.BytesIO()
                    with pd.ExcelWriter(out, engine='xlsxwriter') as wr:
                        df.to_excel(wr, index=False)
                    zf.writestr(f"Tayyor_{f.name.replace('.pdf', '.xlsx')}", out.getvalue())
                except: st.error(f"{f.name} файлида хатолик!")

        st.success("Ҳисоблаш якунланди!")
        st.download_button("📥 ZIP ЮКЛАБ ОЛИШ", zip_buffer.getvalue(), "Natijalar.zip", use_container_width=True)

st.markdown('<div class="footer-box">Боғланиш: <br><b>📞 +998 88 754 98 96</b></div>', unsafe_allow_html=True)
