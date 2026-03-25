import streamlit as st
import pandas as pd
import io
import re
import math
import pdfplumber
import zipfile

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

# 3. "ЖОНЛИ САВДО" АЛГОРИТМИ
def get_pack_size(name):
    name_upper = str(name).upper()
    # Салфетка ва чойларни текшириш (улар доналаб сотилмайди)
    not_for_pieces = ["САЛФЕТКА", "ЧОЙ", "CHAY", "SALFETKA", "МАРЛЯ", "БИНТ"]
    if any(word in name_upper for word in not_for_pieces):
        return 1
    
    match = re.search(r'[N№](\d+)', name_upper)
    return int(match.group(1)) if match else 1

def calculate_prices(cost, pack_size, name):
    unit_cost = cost / pack_size
    # Сиз айтган 19.0% хавфсиз чегара (20% дан ошмаслик учун)
    safe_limit = unit_cost * 1.19 
    
    # 1. Аввал 1000 сўмлик яхлитликни кўрамиз (Энг қулайи)
    res_unit = math.ceil((unit_cost * 1.14) / 1000) * 1000
    
    # 2. Агар 19% дан ошса, 500 га тушамиз
    if res_unit > safe_limit:
        res_unit = math.ceil((unit_cost * 1.12) / 500) * 500
        
    # 3. Агар яна ошса, 100 га тушамиз
    if res_unit > safe_limit:
        res_unit = math.ceil((unit_cost * 1.10) / 100) * 100
        
    # 4. Охирги чора: 19% ичида 100 сўмлик энг баланд нарх
    if res_unit > safe_limit:
        res_unit = math.floor(safe_limit / 100) * 100

    pachka_final = res_unit * pack_size
    dona_final = res_unit
    real_markup = ((pachka_final / cost) - 1) * 100 if cost > 0 else 0
    
    return int(pachka_final), int(dona_final), real_markup

ASOSIY ISHCHI QISM
st.markdown("<h1 style='color: white; text-shadow: 2px 2px 8px black; text-align: center;'>📋 Файлларни ҳисоблаш</h1>", unsafe_allow_html=True)
t1, t2 = st.tabs(["📊 Excel", "📄 PDF"])

def run_logic(df, filename):
    df = df.fillna(0)
    cols = df.columns.tolist()
    c1, c2 = st.columns(2)
    cn = c1.selectbox("Дори номи устуни", cols, key=f"n_{filename}")
    cc = c2.selectbox("Таннарх устуни", cols, index=min(3, len(cols)-1), key=f"c_{filename}")
    
    if st.button("🚀 Ҳисоблаш", key=f"btn_{filename}", use_container_width=True):
        p_l, d_l, m_l = [], [], []
        for _, row in df.iterrows():
            try:
                v = str(row[cc]).replace(' ', '').replace(',', '.')
                cost = float(re.sub(r'[^\d.]', '', v))
                size = get_pack_size(row[cn])
                pp, dd, mm = calculate_prices(cost, size)
                p_l.append(pp); d_l.append(dd); m_l.append(f"{mm:.2f}%")
            except:
                p_l.append(0); d_l.append(0); m_l.append("0%")
        
        df['Pachka Sotuv'] = p_l
        df['Dona Narxi'] = d_l
        df['Наценка'] = m_l
        
        st.success("✅ Ҳисобланди!")
        st.dataframe(df[['Pachka Sotuv', 'Dona Narxi', 'Наценка']].head(15))
        
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine='xlsxwriter') as wr:
            df.to_excel(wr, index=False)
        st.download_button("📥 Натижани юклаш", out.getvalue(), f"Tayyor_{filename}.xlsx", use_container_width=True)

with t1:
    ex = st.file_uploader("📂 Excel файлни танланг", type=['xlsx'], key="main_ex")
    if ex:
        run_logic(pd.read_excel(ex), ex.name)

with t2:
    pdff = st.file_uploader("📂 PDF фактурани танланг", type=['pdf'], key="main_pdf")
    if pdff:
        with pdfplumber.open(pdff) as p:
            all_t = []
            for pg in p.pages:
                tbl = pg.extract_table()
                if tbl: all_t.extend(tbl)
            if all_t:
                df_pdf = pd.DataFrame(all_t[1:], columns=all_t[0])
                run_logic(df_pdf, pdff.name)
