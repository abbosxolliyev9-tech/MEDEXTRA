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
        /* Rasmda chizilgan joy (Login tugmasi pasti) uchun maxsus blok */
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

# 3. GOOGLE SHEETS O'QISH
SHEET_URL = "https://docs.google.com/spreadsheets/d/1XyO5EqqDonEfQnmqr8j7SQNbVcx2SC93txhFVHoDGQA/export?format=csv"

def load_users_data():
    try:
        # TTL=0 qildimki, jadvalga o'zgartirish kiritsangiz darrov saytda ham o'zgarsin
        return pd.read_csv(SHEET_URL)
    except:
        return pd.DataFrame(columns=['phone', 'password', 'name', 'status'])

# 4. MATEMATIK MANTIQ (O'zgarmagan, aniq hisoblaydi)
def get_pack_size(name):
    match = re.search(r'[N№](\d+)', str(name).upper())
    return int(match.group(1)) if match else 1

def calculate_prices(cost, pack_size):
    pachka_raw = cost * 1.12
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
        login_u = st.text_input("Логин / Телефон", key="u_field")
        login_p = st.text_input("Парол", type="password", key="p_field")
        
        if st.button("КИРИШ"):
            users_df = load_users_data()
            entered_hash = hashlib.sha256(login_p.encode()).hexdigest()
            
            user_row = users_df[users_df['phone'].astype(str) == str(login_u)]
            
            if not user_row.empty:
                db_pass = str(user_row.iloc[0]['password'])
                # Ham shifrlangan, ham oddiy parolga tekshiradi
                if db_pass == entered_hash or db_pass == login_p:
                    st.session_state["auth"] = True
                    st.rerun()
                else:
                    st.error("Парол хато!")
            else:
                st.error("Бундай фойдаланувчи топилмади!")
        
        # SIZ CHIZGAN JOYDAGI MATN
        st.markdown('<div class="contact-box">📞 Боғланиш учун: +998 88 754 98 96</div>', unsafe_allow_html=True)

    with tab_reg:
        st.info("Рўйхатдан ўтиш учун админ билан боғланинг.")
        st.markdown('<div class="contact-box">📞 Админ: +998 88 754 98 96</div>', unsafe_allow_html=True)
    
    st.stop()

# 6. ASOSIY ISHCHI QISM (KIRGANDAN KEYIN)
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
                            data = []
                            for pg in p.pages:
                                if pg.extract_table(): data.extend(pg.extract_table())
                            df = pd.DataFrame(data[1:], columns=data[0])
                    
                    p_list, d_list = [], []
                    for _, row in df.iterrows():
                        try:
                            # 4-ustunni (D) tannarx deb oladi
                            cost = float(re.sub(r'[^\d.]', '', str(row.iloc[3]).replace(',','.')))
                            p_p, d_d = calculate_prices(cost, get_pack_size(row.iloc[0]))
                            p_list.append(p_p); d_list.append(d_d)
                        except:
                            p_list.append(0); d_list.append(0)
                    
                    df['Sotuv_Pachka'] = p_list
                    df['Sotuv_Dona'] = d_list
                    
                    out = io.BytesIO()
                    with pd.ExcelWriter(out, engine='xlsxwriter') as wr:
                        df.to_excel(wr, index=False)
                    zf.writestr(f"Tayyor_{f.name.replace('.pdf','.xlsx')}", out.getvalue())
                except:
                    continue
        
        st.download_button("📥 НАТИЖАНИ ЮКЛАШ (ZIP)", zip_buf.getvalue(), "Natijalar.zip")

st.markdown('<div class="contact-box">📞 Боғланиш учун: +998 88 754 98 96</div>', unsafe_allow_html=True)
