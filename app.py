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

# 2. DATABASE FUNKSIYALARI
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

# 3. DIZAYN (CSS)
def add_custom_style():
    bg_image = "https://raw.githubusercontent.com/abbosxolliyev9-tech/MEDEXTRA/main/pexels-eren-34577902.jpg"
    st.markdown(f"""
        <style>
        .stApp {{ background-image: url("{bg_image}"); background-size: cover; background-position: center; }}
        .stTabs [data-baseweb="tab-list"] {{ background-color: #004a99; border-radius: 10px; padding: 5px; }}
        .stTabs [data-baseweb="tab"] {{ color: white !important; font-weight: bold; }}
        .blue-label {{ background-color: #004a99; color: white !important; padding: 8px 15px; border-radius: 5px; font-weight: bold; text-align: center; margin-bottom: 10px; }}
        label {{ background-color: #004a99 !important; color: white !important; padding: 2px 10px !important; border-radius: 4px !important; font-weight: bold !important; }}
        .stButton>button {{ background-color: #004a99 !important; color: white !important; font-weight: bold !important; border-radius: 8px !important; }}
        .footer-box {{ background-color: #004a99; color: white !important; padding: 10px; border-radius: 5px; text-align: center; margin-top: 20px; }}
        </style>
        """, unsafe_allow_html=True)

add_custom_style()

# 4. MATEMATIK VA HISOB-KITOB MANTIQI
def get_pack_size(name):
    """Dori nomidan № sonini qidirish"""
    match = re.search(r'[N№](\d+)', str(name).upper())
    return int(match.group(1)) if match else 1

def calculate_prices(cost, pack_size):
    # 1. Tannarxga 12% ustama qo'shish
    raw_price = cost * 1.12
    
    # 2. Pachka narxini 1000 so'mga TEPAGA yaxlitlash
    pachka_final = math.ceil(raw_price / 1000) * 1000
    
    # 3. Dona narxini hisoblash
    if pack_size > 1:
        # Pachka narxini dona soniga bo'lib, 100 so'mga TEPAGA yaxlitlash
        dona_raw = pachka_final / pack_size
        dona_final = math.ceil(dona_raw / 100) * 100
    else:
        # №1 bo'lsa, dona narxi pachka narxi bilan bir xil
        dona_final = pachka_final
        
    # 4. Haqiqiy ustama foizini qaytarish
    real_markup = ((pachka_final / cost) - 1) * 100 if cost > 0 else 0
    
    return pachka_final, dona_final, real_markup

# 5. LOGIN TIZIMI
if "auth" not in st.session_state: st.session_state["auth"] = False

if not st.session_state["auth"]:
    tab_log, tab_reg = st.tabs(["🔑 КИРИШ", "📝 РЎЙХАТДАН ЎТИШ"])
    
    with tab_reg:
        st.markdown('<div class="blue-label">Янги фойдаланувчи</div>', unsafe_allow_html=True)
        reg_name = st.text_input("Исмингиз", key="reg_name")
        reg_phone = st.text_input("Телефон (масалан: 991234567)", key="reg_phone")
        reg_pass = st.text_input("Парол ўйлаб топинг", type="password", key="reg_pass")
        if st.button("РЎЙХАТДАН ЎТИШ"):
            if reg_phone and reg_pass:
                conn = sqlite3.connect('medextra_users.db')
                c = conn.cursor()
                try:
                    hashed = hashlib.sha256(reg_pass.encode()).hexdigest()
                    c.execute('INSERT INTO users VALUES (?,?,?,?,?)', (reg_phone, hashed, reg_name, '', 0))
                    conn.commit()
                    st.success("✅ Рўйхатdan o'tdingiz! Admin tasdiqlashini kuting.")
                except: st.error("❌ Bu raqam band!")
                conn.close()

    with tab_log:
        st.markdown('<div class="blue-label">Тизимга кириш</div>', unsafe_allow_html=True)
        login_u = st.text_input("Телефон/Логин", key="login_u")
        login_p = st.text_input("Парол", type="password", key="login_p")
        if st.button("КИРИШ", use_container_width=True):
            conn = sqlite3.connect('medextra_users.db')
            c = conn.cursor()
            hashed = hashlib.sha256(login_p.encode()).hexdigest()
            c.execute('SELECT * FROM users WHERE phone=? AND password=?', (login_u, hashed))
            user = c.fetchone()
            if user:
                if user[4] == 0:
                    st.warning("⏳ Hisobingiz hali faollashtirilmagan.")
                else:
                    new_sid = str(uuid.uuid4())
                    c.execute('UPDATE users SET session_id=? WHERE phone=?', (new_sid, login_u))
                    conn.commit()
                    st.session_state.update({"auth": True, "user": login_u, "sid": new_sid, "role": user[4]})
                    st.rerun()
            else: st.error("❌ Login yoki parol xato!")
            conn.close()
    st.markdown('<div class="footer-box">Боғланиш: <br><b>📞 +998 88 754 98 96</b></div>', unsafe_allow_html=True)
    st.stop()

# 6. SEANS VA ADMIN NAZORATI
conn = sqlite3.connect('medextra_users.db')
c = conn.cursor()
c.execute('SELECT session_id, status FROM users WHERE phone=?', (st.session_state["user"],))
db_res = c.fetchone()
conn.close()

if db_res and db_res[0] != st.session_state["sid"]:
    st.error("❗ Boshqa qurilmadan kirildi! Tizimdan chiqarildingiz.")
    st.session_state["auth"] = False
    st.stop()

if st.session_state.get("role") == 9:
    with st.expander("🛠 АДМИН ПАНЕЛИ"):
        conn = sqlite3.connect('medextra_users.db')
        c = conn.cursor()
        c.execute('SELECT phone, name FROM users WHERE status=0')
        pending = c.fetchall()
        if pending:
            for p_user in pending:
                col_u, col_b = st.columns([3, 1])
                col_u.write(f"👤 {p_user[1]} ({p_user[0]})")
                if col_b.button("✅ Тасдиқлаш", key=p_user[0]):
                    c.execute('UPDATE users SET status=1 WHERE phone=?', (p_user[0],))
                    conn.commit()
                    st.rerun()
        else: st.write("Yangi so'rovlar yo'q.")
        conn.close()

# 7. ASOSIY ISHCHI QISM (KO'P FAYLLI VA ZIP TIZIMI)
st.markdown("<h1 style='color: white; text-shadow: 2px 2px 8px black; text-align: center;'>📋 Файлларни тўплам бўлиб ҳисоблаш</h1>", unsafe_allow_html=True)

uploaded_files = st.file_uploader("Excel yoki PDF fayllarni tanlang (bir nechta bo'lishi mumkin)", 
                                  type=['xlsx', 'pdf'], 
                                  accept_multiple_files=True)

if uploaded_files:
    st.info(f"Yulangan fayllar soni: {len(uploaded_files)} ta")
    
    # Ustunlarni aniqlash uchun birinchi faylni o'qish
    try:
        if uploaded_files[0].name.endswith('xlsx'):
            temp_df = pd.read_excel(uploaded_files[0])
        else:
            with pdfplumber.open(uploaded_files[0]) as p:
                tbl = p.pages[0].extract_table()
                temp_df = pd.DataFrame(tbl[1:], columns=tbl[0]) if tbl else pd.DataFrame()
        cols = temp_df.columns.tolist()
    except:
        cols = ["Ustun topilmadi"]

    st.markdown('<div class="blue-label">Устунларни созлаш</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    col_n = c1.selectbox("Dori nomi ustuni:", cols, index=0)
    col_c = c2.selectbox("Tannarx ustuni:", cols, index=min(3, len(cols)-1))

    if st.button("🚀 BARCHA FAYLLARNI BIRDAНИГА HISOBLASH", use_container_width=True):
        processed_files = [] 
        
        for uploaded_file in uploaded_files:
            try:
                if uploaded_file.name.endswith('xlsx'):
                    df = pd.read_excel(uploaded_file)
                else:
                    with pdfplumber.open(uploaded_file) as p:
                        all_t = []
                        for pg in p.pages:
                            tbl = pg.extract_table()
                            if tbl: all_t.extend(tbl)
                        df = pd.DataFrame(all_t[1:], columns=all_t[0]) if all_t else pd.DataFrame()

                if not df.empty:
                    df = df.fillna(0)
                    p_l, d_l, m_l = [], [], []
                    
                    for _, row in df.iterrows():
                        try:
                            v = str(row[col_c]).replace(' ', '').replace(',', '.')
                            cost = float(re.sub(r'[^\d.]', '', v))
                            size = get_pack_size(row[col_n])
                            pp, dd, mm = calculate_prices(cost, size)
                            p_l.append(pp); d_l.append(dd); m_l.append(f"{mm:.2f}%")
                        except:
                            p_l.append(0); d_l.append(0); m_l.append("0%")
                    
                    df['Pachka Sotuv'] = p_l
                    df['Dona Narxi'] = d_l
                    df['Ustama %'] = m_l
                    
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as wr:
                        df.to_excel(wr, index=False)
                    processed_files.append((uploaded_file.name, output.getvalue()))
            except Exception as e:
                st.error(f"❌ {uploaded_file.name} hisoblashda xato: {e}")

        if processed_files:
            if len(processed_files) == 1:
                st.download_button(f"📥 {processed_files[0][0]} yuklash", 
                                   processed_files[0][1], 
                                   f"Tayyor_{processed_files[0][0]}", use_container_width=True)
            else:
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    for name, data in processed_files:
                        zf.writestr(f"Tayyor_{name}.xlsx", data)
                
                st.success("✅ Barcha fayllar tayyor!")
                st.download_button("📥 BARCHA TAYYOR FAYLLARNI YUKLASH (ZIP)", 
                                   zip_buffer.getvalue(), 
                                   "Medextra_Fayllar.zip", use_container_width=True)
