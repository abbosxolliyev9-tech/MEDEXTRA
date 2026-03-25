import streamlit as st
import pandas as pd
import io
import re
import math
import pdfplumber
import zipfile

# 1. САҲИФА СОЗЛАМАЛАРИ
st.set_page_config(page_title="MEDEXTRA", page_icon="💊", layout="centered")

# 2. ЭСКИ ДИЗАЙННИ ТИКЛАШ (Кўк фон ва олдинги кўриниш)
def add_custom_style():
    # Орқа фонд расми
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
        .stSelectbox label, .stFileUploader label {{
            color: white !important;
            font-weight: bold;
            background-color: rgba(0, 74, 153, 0.8);
            padding: 5px 15px;
            border-radius: 5px;
        }}
        /* Киритиш майдонлари учун */
        .stTextInput input {{
            background-color: white !important;
        }}
        </style>
        """, unsafe_allow_html=True)

add_custom_style()

# 3. ЯНГИ МАНТИҚ (1000 -> 500 -> 100 ва 18.99% чегара)
def get_pack_size(name):
    match = re.search(r'[N№](\d+)', str(name).upper())
    return int(match.group(1)) if match else 1

def calculate_prices(cost, pack_size):
    unit_cost = cost / pack_size
    max_allowed_unit = unit_cost * 1.1899  # 18.99% максимал чегара
    target_unit = unit_cost * 1.12        # 12% базавий устама
    
    # Қадамма-қадам яхлитлаш
    # 1. 1000 сўмга яхлитлаб кўрамиз
    res_unit = math.ceil(target_unit / 1000) * 1000
    
    if res_unit > max_allowed_unit:
        # 2. 500 сўмга яхлитлаб кўрамиз
        res_unit = math.ceil(target_unit / 500) * 500
        
    if res_unit > max_allowed_unit:
        # 3. 100 сўмга яхлитлаб кўрамиз
        res_unit = math.ceil(target_unit / 100) * 100
        
    if res_unit > max_allowed_unit:
        # Охирги чора: Лимит ичида 100 сўмлик энг яқин паст нарх
        res_unit = math.floor(max_allowed_unit / 100) * 100

    pachka_final = res_unit * pack_size
    dona_final = res_unit
    real_markup = ((pachka_final / cost) - 1) * 100 if cost > 0 else 0
    
    return int(pachka_final), int(dona_final), real_markup

# 4. ЛОГИН ҚИСМИ
if "auth" not in st.session_state: st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.markdown('<div class="blue-label">💊 MEDEXTRA LOGIN</div>', unsafe_allow_html=True)
    u = st.text_input("Логин")
    p = st.text_input("Парол", type="password")
    if st.button("КИРИШ"):
        if u == "admin" and p == "Abbos96":
            st.session_state["auth"] = True
            st.rerun()
        else:
            st.error("Хато!")
    st.stop()

# 5. ИШЧИ МАЙДОН
st.markdown('<div class="blue-label">📋 ФАЙЛЛАРНИ ҲИСОБЛАШ</div>', unsafe_allow_html=True)

files = st.file_uploader("Excel ёки PDF танланг", type=['xlsx', 'pdf'], accept_multiple_files=True)

if files:
    try:
        if files[0].name.endswith('xlsx'):
            df_temp = pd.read_excel(files[0])
            cols = df_temp.columns.tolist()
        else:
            cols = ["Дори номи", "Таннарх"]
    except:
        cols = ["A", "B", "C", "D"]

    col_n = st.selectbox("💊 Дори номи устуни", cols, index=0)
    col_c = st.selectbox("💰 Таннарх устуни", cols, index=min(3, len(cols)-1))

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
                p_list, d_list, m_list = [], [], []
                
                for _, row in df.iterrows():
                    try:
                        val = str(row[col_c]).replace(' ', '').replace(',', '.')
                        cost = float(re.sub(
