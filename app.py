import streamlit as st
import pandas as pd
import io
import re
import math

# 1. САҲИФА СОЗЛАМАЛАРИ
st.set_page_config(page_title="MEDEXTRA", page_icon="💊", layout="centered")

# 2. ЭСКИ ДИЗАЙН (Кўк фон ва олдинги чиройли кўриниш)
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
        .stSelectbox label, .stFileUploader label {{
            color: white !important;
            font-weight: bold;
            background-color: rgba(0, 74, 153, 0.8);
            padding: 5px 15px;
            border-radius: 5px;
        }}
        </style>
        """, unsafe_allow_html=True)

add_custom_style()

# 3. МУКАММАЛ ҲИСОБ-КИТОБ МАНТИҒИ (1000 -> 500 -> 100)
def get_pack_size(name):
    name_upper = str(name).upper()
    not_for_pieces = ["САЛФЕТКА", "ЧОЙ", "CHAY", "SALFETKA", "МАРЛЯ", "БИНТ"]
    if any(word in name_upper for word in not_for_pieces):
        return 1
    match = re.search(r'[N№](\d+)', name_upper)
    return int(match.group(1)) if match else 1

def calculate_prices(cost, pack_size):
    unit_cost = cost / pack_size
    safe_limit_unit = unit_cost * 1.19  # 19% хавфсиз чегара
    
    # 1. 1000 га яхлитлаб кўрамиз
    res_unit = math.ceil((unit_cost * 1.14) / 1000) * 1000
    if res_unit > safe_limit_unit:
        res_unit = math.ceil((unit_cost * 1.12) / 500) * 500
    if res_unit > safe_limit_unit:
        res_unit = math.ceil((unit_cost * 1.10) / 100) * 100
    if res_unit > safe_limit_unit:
        res_unit = math.floor(safe_limit_unit / 100) * 100

    pachka_final = int(res_unit * pack_size)
    dona_final = int(res_unit)
    real_markup = ((pachka_final / cost) - 1) * 100 if cost > 0 else 0
    return pachka_final, dona_final, real_markup

# 4. ТИЗИМГА КИРИШ
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.markdown('<div class="blue-label">💊 MEDEXTRA КИРИШ</div>', unsafe_allow_html=True)
    u = st.text_input("Логин")
    p = st.text_input("Парол", type="password")
    if st.button("КИРИШ"):
        if u == "admin" and p == "Abbos96":
            st.session_state["auth"] = True
            st.rerun()
        else:
            st.error("Логин ёки парол хато!")
    st.stop()

# 5. ИШЧИ МАЙДОН
st.markdown('<div class="blue-label">📋 ФАЙЛЛАРНИ ҲИСОБЛАШ</div>', unsafe_allow_html=True)
files = st.file_uploader("Excel файлини танланг", type=['xlsx'], accept_multiple_files=True)

if files:
    try:
        df_sample = pd.read_excel(files[0])
        cols = df_sample.columns.tolist()
        
        c1, c2 = st.columns(2)
        col_n = c1.selectbox("💊 Дори номи устуни", cols, index=0)
        col_c = c2.selectbox("💰 Таннарх устуни", cols, index=min(3, len(cols)-1))

        if st.button("🚀 ҲИСОБЛАШ"):
            for f in files:
                df = pd.read_excel(f).fillna(0)
                p_l, d_l, m_l = [], [], []
                
                for _, row in df.iterrows():
                    try:
                        name = str(row[col_n])
                        # Таннархни тозалаш
                        val = str(row[col_c]).replace(' ', '').replace(',', '.')
                        cost = float(re.sub(r'[^\d.]', '', val))
                        size = get_pack_size(name)
                        
                        p_p, d_p, m_p = calculate_prices(cost, size)
                        p_l.append(p_p)
                        d_l.append(d_p)
                        m_l.append(f"{m_p:.1f}%")
                    except:
                        p_l.append(0); d_l.append(0); m_l.append("0%")
                
                df['Sotuv_Pachka'] = p_l
                df['Sotuv_Dona'] = d_l
                df['Ustama_%'] = m_l
                
                # Excel қилиш ва юклаш тугмаси
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False)
                
                st.download_button(f"📥 {f.name} (ТАЙЁР)", output.getvalue(), f"Tayyor_{f.name}")
    except Exception as e:
        st.error(f"Хатолик юз берди: {e}")
