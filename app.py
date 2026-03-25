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

# 2. ДИЗАЙН (Эски кўк услубдаги олдинги кўриниш)
def add_custom_style():
    # Орқа фонд учун расм (олдингидек)
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
            text-shadow: 1px 1px 2px black;
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
        .stSelectbox label, .stFileUploader label {{
            color: white !important;
            font-weight: bold;
            background-color: rgba(0, 74, 153, 0.7);
            padding: 2px 10px;
            border-radius: 5px;
        }}
        </style>
        """, unsafe_allow_html=True)

add_custom_style()

# 3. АСОСИЙ ҲИСОБ-КИТОБ МАНТИҒИ (1000 -> 500 -> 100)
def get_pack_size(name):
    match = re.search(r'[N№](\d+)', str(name).upper())
    return int(match.group(1)) if match else 1

def calculate_prices(cost, pack_size):
    unit_cost = cost / pack_size
    max_allowed_unit = unit_cost * 1.18  # 18% лимит
    target_unit = unit_cost * 1.12       # 12% базавий устама
    
    # 1000 сўмга яхлитлаб кўриш
    res_unit = math.ceil(target_unit / 1000) * 1000
    
    if res_unit > max_allowed_unit:
        # 500 сўмга яхлитлаб кўриш
        res_unit = math.ceil(target_unit / 500) * 500
        
    if res_unit > max_allowed_unit:
        # 100 сўмга яхлитлаб кўриш
        res_unit = math.ceil(target_unit / 100) * 100
        
    if res_unit > max_allowed_unit:
        # Чегарадан ошмаслик учун 100 сўмлик энг яқин паст нарх
        res_unit = math.floor(max_allowed_unit / 100) * 100

    pachka_final = res_unit * pack_size
    dona_final = res_unit
    real_markup = ((pachka_final / cost) - 1) * 100 if cost > 0 else 0
    
    return int(pachka_final), int(dona_final), real_markup

# 4. ЛОГИН ТИЗИМИ
if "auth" not in st.session_state: st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.markdown('<div class="blue-label">💊 MEDEXTRA LOGIN</div>', unsafe_allow_html=True)
    u = st.text_input("Логин")
    p = st.text_input("Парол", type="password")
    if st.button("КИРИШ"):
        if u == "admin" and p == "Abbos96":
            st.session_state["auth"] = True
            st.rerun()
    st.stop()

# 5. ИШЧИ МАЙДОН
st.markdown('<div class="blue-label">📋 ФАЙЛЛАРНИ ҲИСОБЛАШ</div>', unsafe_allow_html=True)

files = st.file_uploader("Excel ёки PDF танланг", type=['xlsx', 'pdf'], accept_multiple_files=True)

if files:
    # Устунларни аниқлаш
    try:
        if files[0].name.endswith('xlsx'):
            df_temp = pd.read_excel(files[0])
            cols = df_temp.columns.tolist()
        else:
            cols = ["Дори номи", "Таннарх"]
    except:
        cols = ["A", "B", "C", "D"]

    col_n = st.selectbox("Дори номи устуни", cols, index=0)
    col_c = st.selectbox("Таннарх устуни", cols, index=min(3, len(cols)-1))

    if st.button("🚀 ҲИСОБЛАШНИ БОШЛАШ"):
        processed = []
        for f in files:
            try:
                if f.name.endswith('xlsx'):
                    df = pd.read_excel(f)
                else:
                    with pdfplumber.open(f) as pdf:
                        tbl = []
                        for page in pdf.pages:
                            rows = page.extract_table()
                            if rows: tbl.extend(rows)
                        df = pd.DataFrame(tbl[1:], columns=tbl[0])
                
                df = df.fillna(0)
                p_l, d_l, m_l = [], [], []
                
                for _, row in df.iterrows():
                    try:
                        val = str(row[col_c]).replace(' ', '').replace(',', '.')
                        cost = float(re.sub(r'[^\d.]', '', val))
                        size = get_pack_size(row[col_n])
                        
                        p_p, d_p, m_p = calculate_prices(cost, size)
                        
                        p_l.append(p_p)
                        d_l.append(d_p)
                        m_l.append(f"{m_p:.1f}%")
                    except:
                        p_l.append(0); d_l.append(0); m_l.append("0%")
                
                df['Sotuv_Pachka'] = p_l
                df['Sotuv_Dona'] = d_l
                df['Ustama_%'] = m_l
                
                out = io.BytesIO()
                with pd.ExcelWriter(out, engine='xlsxwriter') as wr:
                    df.to_excel(wr, index=False)
                processed.append((f.name, out.getvalue()))
            except:
                continue

        if processed:
            if len(processed) > 1:
                zip_out = io.BytesIO()
                with zipfile.ZipFile(zip_out, "w") as zf:
                    for name, data in processed:
                        zf.writestr(f"Tayyor_{name}.xlsx", data)
                st.download_button("📥 ZIP ЮКЛАШ", zip_out.getvalue(), "Natijalar.zip")
            else:
                st.download_button("📥 EXCEL ЮКЛАШ", processed[0][1], f"Tayyor_{processed[0][0]}")

st.info("Юқоридаги код 18% лимит ва 1000/500/100 яхлитлаш мантиғида ишлайди.")
