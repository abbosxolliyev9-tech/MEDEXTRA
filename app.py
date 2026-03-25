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
st.set_page_config(page_title="MEDEXTRA PRO", page_icon="💊", layout="centered")

# 2. МАЪЛУМОТЛАР БАЗАСИ (Login учун)
def init_db():
    conn = sqlite3.connect('medextra_users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (phone TEXT PRIMARY KEY, password TEXT, name TEXT, session_id TEXT, status INTEGER)''')
    admin_pass = hashlib.sha256("Abbos96".encode()).hexdigest()
    c.execute('INSERT OR IGNORE INTO users VALUES (?,?,?,?,?)', ('admin', admin_pass, 'ADMIN', '', 9))
    conn.commit()
    conn.close()

init_db()

# 3. ДОРИХОНА МАНТИҒИ (18% фойда ва 1000/100 сўмлик яхлитлаш)
def get_pack_size(name):
    """Дори номидан N ёки № белгисидан кейинги сонни топади"""
    match = re.search(r'[N№](\d+)', str(name).upper())
    return int(match.group(1)) if match else 1

def calculate_prices(cost, pack_size):
    """Сиз айтган махсус ҳисоблаш алгоритми"""
    # Максимал чегара - 18% фойда
    max_allowed = cost * 1.18
    
    # 1. Аввал 1000 сўмгача ТЕПАГА яхлитлаб кўрамиз
    # (Одатда 12% устама билан бошланади)
    pachka_final = math.ceil((cost * 1.12) / 1000) * 1000
    
    # 2. Агар 1000 га яхлитлаш 18% дан ошиб кетса
    if pachka_final > max_allowed:
        # 18% ичида қоладиган энг катта сонни 100 сўмлик қадам билан топамиз
        pachka_final = math.floor(max_allowed / 100) * 100
    
    # 3. Дона (штук) нархини ҳисоблаш
    if pack_size > 1:
        dona_raw = pachka_final / pack_size
        # Дона нархини 1000 гача яхлитлаб кўрамиз
        dona_final = math.ceil(dona_raw / 1000) * 1000
        
        # Агар донани 1000 га яхлитлаш 18% дан ошириб юборса (пачкага нисбатан)
        # ёки нотабиий қиммат бўлса, 100 сўмлик қадамга ўтамиз
        if (dona_final * pack_size) > (pachka_final * 1.15):
            dona_final = math.ceil(dona_raw / 100) * 100
    else:
        dona_final = pachka_final
        
    real_markup = ((pachka_final / cost) - 1) * 100 if cost > 0 else 0
    return pachka_final, dona_final, real_markup

# 4. ДИЗАЙН (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    .main-title { color: #004a99; text-align: center; font-weight: bold; text-shadow: 1px 1px 2px white; }
    .stButton>button { background-color: #004a99 !important; color: white !important; font-weight: bold; border-radius: 10px; height: 50px; }
    .success-box { background-color: #d4edda; padding: 15px; border-radius: 10px; border: 1px solid #c3e6cb; color: #155724; }
    </style>
    """, unsafe_allow_html=True)

# 5. КИРИШ ТИЗИМИ
if "auth" not in st.session_state: st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.markdown("<h1 class='main-title'>💊 MEDEXTRA PRO TIZIMI</h1>", unsafe_allow_html=True)
    with st.container():
        u = st.text_input("Логин/Телефон")
        p = st.text_input("Парол", type="password")
        if st.button("ТИЗИМГА КИРИШ"):
            if u == "admin" and p == "Abbos96": # Ўзингизга мосланг
                st.session_state["auth"] = True
                st.session_state["
