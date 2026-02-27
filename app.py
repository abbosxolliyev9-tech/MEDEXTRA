import streamlit as st
import pandas as pd
import io
import re
import math
import pdfplumber

# 1. SAHIFA SOZLAMALARI
st.set_page_config(page_title="MEDEXTRA", page_icon="💊", layout="centered")

# 2. MATEMATIK MANTIQ (O'zgarmagan)
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

# 3. DIZAYN (Yozuvlarni tiniqlashtirish uchun maxsus CSS)
def add_custom_style():
    bg_image = "https://raw.githubusercontent.com/abbosxolliyev9-tech/MEDEXTRA/main/pexels-eren-34577902.jpg"
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("{bg_image}");
            background-size: cover;
            background-position: center;
        }}
        /* Bo'lim yozuvlarini (Tabs) ko'k fonda aniq qilish */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: #004a99;
            border-radius: 10px;
            padding: 5px;
            gap: 10px;
        }}
        .stTabs [data-baseweb="tab"] {{
            color: white !important;
            font-weight: bold;
            border-radius: 5px;
        }}
        /* Fayl yuklash va dori tanlash label'larini tiniq qilish */
        .stFileUploader label, .stSelectbox label {{
            background-color: #004a99 !important;
            color: white !important;
            padding: 5px 15px !important;
            border-radius: 5px !important;
            font-weight: bold !important;
            display: inline-block !important;
            margin-bottom: 8px !important;
        }}
        /* Login qismidagi ko'k label'lar */
        .blue-label {{
            background-color: #004a99;
            color: white !important;
            padding: 8px 20px;
            border-radius: 5px;
            display: inline-block;
            font-weight: bold;
            margin-bottom: 8px;
            text-align: center;
        }}
        .stButton>button {{
            background-color: #004a99 !important;
            color: white !important;
            border-radius: 10px !important;
            font-weight: bold !important;
        }}
        .footer-box {{
            background-color: #004a99;
            color: white !important;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
        }}
        </style>
        """, unsafe_allow_html=True)

add_custom_style()

# 4. LOGIN TIZIMI
if "auth" not in st.session_state: st.session_state["auth"] = False
if not st.session_state["auth"]:
    col1, col2, col3 = st.columns([0.1, 1, 0.1])
    with col2:
        st.write("<br><br>", unsafe_allow_html=True)
        st.markdown('<div class="blue-label" style="font-size: 30px; width: 100%;">💊 MEDEXTRA</div>', unsafe_allow_html=True)
        st.markdown('<div class="blue-label" style="width: 100%;">Фармацевтика тизимига кириш</div>', unsafe_allow_html=True)
        u = st.text_input("Логин", value="admin")
        p = st.text_input("Парол", type="password")
        if st.button("ТИЗИМГА КИРИШ", use_container_width=True):
            if u == "admin" and p == "Abbos96":
                st.session_state["auth"] = True
                st.rerun()
            else: st.error("❌ Логин ёки парол хато!")
        st.markdown('<div class="footer-box">Боғланиш: <br><b>📞 +998 88 754 98 96</b></div>', unsafe_allow_html=True)
    st.stop()

# 5. ASOSIY QISM
st.markdown("<h1 style='color: white; text-shadow: 2px 2px 8px black; text-align: center;'>📋 Файлларни ҳисоблаш</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📊 Excel бўлими", "📄 PDF бўлими"])

def process_data(data_df, f_name):
    data_df = data_df.fillna(0)
    cols = data_df.columns.tolist()
    c1, c2 = st.columns(2)
    col_n = c1.selectbox("Дори номи устуни", cols, key=f"n_{f_name}")
    col_c = c2.selectbox("Таннарх устуни", cols, index=min(3, len(cols)-1), key=f"c_{f_name}")
    
    if st.button("🚀 Ҳисоблаш", key=f"b_{f_name}", use_container_width=True):
        res_p, res_d, res_m = [], [], []
        for _, row in data_df.iterrows():
            try:
                val = str(row[col_c]).replace(' ', '').replace(',', '.')
                cost = float(re.sub(r'[^\d.]', '', val))
                size = get_pack_size(row[col_n])
                p_p, d_d, m_m = calculate_prices(cost, size)
                res_p.append(p_p); res_d.append(d_d); res_m.append(f"{m_m:.2f}%")
            except:
                res_p.append(0); res_d.append(0); res_m.append("0%")
        
        data_df['Pachka Sotuv'] = res_p
        data_df['Dona Narxi'] = res_d
        data_df['Наценка'] = res_m
        
        st.success("✅ Муваффақиятли ҳисобланди!")
        st.dataframe(data_df[['Pachka Sotuv', 'Dona Narxi', 'Наценка']].head(15))
        
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine='xlsxwriter') as wr:
            data_df.to_excel(wr, index=False)
        st.download_button("📥 Натижани Excelда юклаш", out.getvalue(), f"Tayyor_{f_name}.xlsx", use_container_width=True)

with tab1:
    ex = st.file_uploader("📂 Excel файлни танланг", type=['xlsx'], key="ex_up")
    if ex: process_data(pd.read_excel(ex), ex.name)

with tab2:
    pdf = st.file_uploader("📂 PDF фактурани танланг", type=['pdf'], key="pdf_up")
    if pdf:
        with pdfplumber.open(pdf) as p_file:
            all_t = []
            for page in p_file.pages:
                t = page.extract_table()
                if t: all_t.extend(t)
            if all_t:
                process_data(pd.DataFrame(all_t[1:], columns=all_t[0]), pdf.name)
