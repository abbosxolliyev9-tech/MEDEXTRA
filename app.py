import streamlit as st
import pandas as pd
import io
import re
import math
import pdfplumber
import sqlite3
import hashlib
import uuid

# 1. DATABASE SOZLAMALARI
def init_db():
    conn = sqlite3.connect('medextra_users.db')
    c = conn.cursor()
    # status: 0-kutish, 1-aktiv, 9-admin
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (phone TEXT PRIMARY KEY, password TEXT, name TEXT, session_id TEXT, status INTEGER)''')
    # Adminni yaratib qo'yamiz (agar bo'lmasa)
    admin_pass = hashlib.sha256("Abbos96".encode()).hexdigest()
    c.execute('INSERT OR IGNORE INTO users VALUES (?,?,?,?,?)', 
              ('admin', admin_pass, 'ADMIN', '', 9))
    conn.commit()
    conn.close()

init_db()

# 2. DIZAYN (TINIQLASHTIRILGAN)
def add_custom_style():
    bg_image = "https://raw.githubusercontent.com/abbosxolliyev9-tech/MEDEXTRA/main/pexels-eren-34577902.jpg"
    st.markdown(f"""
        <style>
        .stApp {{ background-image: url("{bg_image}"); background-size: cover; background-position: center; }}
        .stTabs [data-baseweb="tab-list"] {{ background-color: #004a99; border-radius: 10px; padding: 5px; }}
        .stTabs [data-baseweb="tab"] {{ color: white !important; font-weight: bold; }}
        .blue-label {{ background-color: #004a99; color: white !important; padding: 8px 15px; border-radius: 5px; font-weight: bold; text-align: center; margin-bottom: 10px; }}
        label {{ background-color: #004a99 !important; color: white !important; padding: 2px 10px !important; border-radius: 4px !important; }}
        .stButton>button {{ background-color: #004a99 !important; color: white !important; font-weight: bold !important; border-radius: 8px !important; }}
        </style>
        """, unsafe_allow_html=True)

add_custom_style()

# 3. MANTIQIY FUNKSIYALAR
def get_pack_size(name):
    match = re.search(r'[N№](\d+)', str(name).upper())
    if match: return int(match.group(1))
    match_alt = re.search(r'(\d+)\s*(ТА|TA|ШТ|шт)', str(name).upper())
    if match_alt: return int(match_alt.group(1))
    return 1

def calculate_prices(cost, pack_size):
    if cost <= 0: return 0, 0, 0
    unit_cost = cost / pack_size
    raw_price = unit_cost * 1.12
    if pack_size == 1:
        final_price = math.ceil(raw_price / 1000) * 1000
        if final_price > (unit_cost * 1.18):
            final_price = math.ceil(raw_price / 100) * 100
    else:
        final_price = math.ceil(raw_price / 100) * 100
    pachka_final = final_price * pack_size
    real_markup = ((pachka_final / cost) - 1) * 100
    return pachka_final, final_price, real_markup

# 4. LOGIN / REGISTRATSIYA
if "auth" not in st.session_state: st.session_state["auth"] = False

if not st.session_state["auth"]:
    tab_log, tab_reg = st.tabs(["🔑 КИРИШ", "📝 РЎЙХАТДАН ЎТИШ"])
    
    with tab_reg:
        st.markdown('<div class="blue-label">Янги фойдаланувчи</div>', unsafe_allow_html=True)
        reg_name = st.text_input("Исмингиз")
        reg_phone = st.text_input("Телефон (масалан: 991234567)")
        reg_pass = st.text_input("Парол ўйлаб топинг", type="password")
        if st.button("РЎЙХАТДАН ЎТИШ"):
            if reg_phone and reg_pass:
                conn = sqlite3.connect('medextra_users.db')
                c = conn.cursor()
                try:
                    hashed = hashlib.sha256(reg_pass.encode()).hexdigest()
                    c.execute('INSERT INTO users VALUES (?,?,?,?,?)', (reg_phone, hashed, reg_name, '', 0))
                    conn.commit()
                    st.success("Рўйхатдан ўтдингиз! Тўловни қилинг ва админ тасдиқлашини кутинг.")
                except: st.error("Бу рақам банд!")
                conn.close()

    with tab_log:
        st.markdown('<div class="blue-label">Тизимга кириш</div>', unsafe_allow_html=True)
        login_u = st.text_input("Телефон")
        login_p = st.text_input("Парол", type="password")
        if st.button("КИРИШ", use_container_width=True):
            conn = sqlite3.connect('medextra_users.db')
            c = conn.cursor()
            hashed = hashlib.sha256(login_p.encode()).hexdigest()
            c.execute('SELECT * FROM users WHERE phone=? AND password=?', (login_u, hashed))
            user = c.fetchone()
            if user:
                if user[4] == 0:
                    st.warning("Ҳисобингиз ҳали фаоллаштирилмаган. Админга боғланинг.")
                else:
                    new_sid = str(uuid.uuid4())
                    c.execute('UPDATE users SET session_id=? WHERE phone=?', (new_sid, login_u))
                    conn.commit()
                    st.session_state["auth"] = True
                    st.session_state["user"] = login_u
                    st.session_state["sid"] = new_sid
                    st.session_state["role"] = user[4]
                    st.rerun()
            else: st.error("Маълумотлар хато!")
            conn.close()
    st.stop()

# 5. ADMIN PANEL (Faqat siz uchun)
if st.session_state.get("role") == 9:
    with st.expander("🛠 АДМИН ПАНЕЛИ"):
        conn = sqlite3.connect('medextra_users.db')
        c = conn.cursor()
        c.execute('SELECT phone, name, status FROM users WHERE status=0')
        pending = c.fetchall()
        if pending:
            for p_user in pending:
                col_u, col_b = st.columns([3, 1])
                col_u.write(f"👤 {p_user[1]} ({p_user[0]})")
                if col_b.button("✅ Тасдиқлаш", key=p_user[0]):
                    c.execute('UPDATE users SET status=1 WHERE phone=?', (p_user[0],))
                    conn.commit()
                    st.rerun()
        else: st.write("Янги сўровлар йўқ.")
        conn.close()

# 6. SEANSNI TEKSHIRISH (Bitta qurilma cheklovi)
conn = sqlite3.connect('medextra_users.db')
c = conn.cursor()
c.execute('SELECT session_id FROM users WHERE phone=?', (st.session_state["user"],))
db_sid = c.fetchone()[0]
conn.close()
if db_sid != st.session_state["sid"]:
    st.error("Бошқа қурилмадан кирилди! Тизимдан чиқарилдингиз.")
    st.session_state["auth"] = False
    st.stop()

# 7. ASOSIY ISHCHI QISM (Excel va PDF)
st.markdown("<h1 style='text-align: center;'>📋 Файлларни ҳисоблаш</h1>", unsafe_allow_html=True)
t1, t2 = st.tabs(["📊 Excel", "📄 PDF"])

def run_logic(df, n):
    df = df.fillna(0)
    cols = df.columns.tolist()
    c1, c2 = st.columns(2)
    cn = c1.selectbox("Номи", cols, key=f"n{n}")
    cc = c2.selectbox("Таннарх", cols, index=min(3, len(cols)-1), key=f"c{n}")
    if st.button("🚀 Ҳисоблаш", key=f"b{n}", use_container_width=True):
        p_l, d_l, m_l = [], [], []
        for _, row in df.iterrows():
            try:
                v = str(row[cc]).replace(' ', '').replace(',', '.')
                cost = float(re.sub(r'[^\d.]', '', v))
                size = get_pack_size(row[cn])
                pp, dd, mm = calculate_prices(cost, size)
                p_l.append(pp); d_l.append(dd); m_l.append(f"{mm:.2f}%")
            except: p_l.append(0); d_l.append(0); m_l.append("0%")
        df['Pachka Sotuv'], df['Dona Narxi'], df['Наценка'] = p_l, d_l, m_l
        st.dataframe(df[['Pachka Sotuv', 'Dona Narxi', 'Наценка']].head(10))
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine='xlsxwriter') as wr: df.to_excel(wr, index=False)
        st.download_button("📥 Юклаш", out.getvalue(), f"Tayyor_{n}.xlsx", use_container_width=True)

with t1:
    ex = st.file_uploader("Excel tanlang", type=['xlsx'])
    if ex: run_logic(pd.read_excel(ex), ex.name)
with t2:
    pdff = st.file_uploader("PDF tanlang", type=['pdf'])
    if pdff:
        with pdfplumber.open(pdff) as p:
            all_t = []
            for pg in p.pages:
                tbl = pg.extract_table()
                if tbl: all_t.extend(tbl)
            if all_t: run_logic(pd.DataFrame(all_t[1:], columns=all_t[0]), pdff.name)
