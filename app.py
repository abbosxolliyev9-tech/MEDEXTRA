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

# 2. DIZAYN
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

# 4. СИЗ АЙТГАН МАТЕМАТИК МАНТИҚ (АЙНАН ЎЗИ)
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
    ustama_foiz = ((pachka_final / cost) - 1) * 100 if cost > 0 else 0
    return pachka_final, int(res_unit), f"{ustama_foiz:.1f}%"

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

# 6. АСОСИЙ ИШЧИ ҚИСМ
st.markdown('<div class="blue-label">📋 ФАЙЛЛАРНИ ҲИСОБЛАШ</div>', unsafe_allow_html=True)
files = st.file_uploader("Excel ёки PDF танланг", accept_multiple_files=True)

if files:
    if st.button("🚀 ҲИСОБЛАШ"):
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w") as zf:
            for f in files:
                try:
                    if f.name.endswith('xlsx'):
                        df = pd.read_excel(f)
                    else:
                        with pdfplumber.open(f) as p:
                            rows = []
                            for pg in p.pages:
                                if pg.extract_table(): rows.extend(pg.extract_table())
                            df = pd.DataFrame(rows[1:], columns=rows[0])
                    
                    p_l, d_l, u_l = [], [], []
                    for _, row in df.iterrows():
                        try:
                            # 4-устунни (D ёки E) таннарх деб олишга ҳаракат қилади
                            cost_val = str(row.iloc[3] if len(row) > 3 else row.iloc[-1])
                            cost = float(re.sub(r'[^\d.]', '', cost_val.replace(',','.')))
                            name = str(row.iloc[0])
                            
                            p_f, d_f, u_f = calculate_prices(cost, get_pack_size(name))
                            p_l.append(p_f); d_l.append(d_f); u_l.append(u_f)
                        except:
                            p_l.append(0); d_l.append(0); u_l.append("0%")
                    
                    df['Sotuv_Pachka'] = p_l
                    df['Sotuv_Dona'] = d_l
                    df['Ustama'] = u_l
                    
                    out = io.BytesIO()
                    with pd.ExcelWriter(out, engine='xlsxwriter') as wr:
                        df.to_excel(wr, index=False)
                    zf.writestr(f"Tayyor_{f.name.replace('.pdf','.xlsx')}", out.getvalue())
                except: continue
        
        st.download_button("📥 НАТИЖАНИ ЮКЛАШ (ZIP)", zip_buf.getvalue(), "Natijalar.zip")

st.markdown('<div class="contact-box">📞 Боғланиш учун: +998 88 754 98 96</div>', unsafe_allow_html=True)
