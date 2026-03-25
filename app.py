import streamlit as st
import pandas as pd
import io
import re
import math
import zipfile

# 1. АСОСИЙ МАНТИҚ - СИЗ АЙТГАН ПРИНЦИП АСОСИДА
def get_pack_size(name):
    match = re.search(r'[N№](\d+)', str(name).upper())
    return int(match.group(1)) if match else 1

def calculate_prices(cost, pack_size):
    # Асл таннарх
    unit_cost = cost / pack_size
    max_allowed_unit = unit_cost * 1.18  # 18% чегара
    
    # Бошланғич устама (12% дан бошлаймиз)
    target_unit = unit_cost * 1.12
    
    # ҚАДАМЛАР БЎЙИЧА ЯХЛИТЛАШ (1000 -> 500 -> 100)
    # 1-қадам: 1000 сўмга яхлитлаб кўрамиз
    res_unit = math.ceil(target_unit / 1000) * 1000
    
    if res_unit > max_allowed_unit:
        # 2-қадам: 500 сўмга яхлитлаб кўрамиз
        res_unit = math.ceil(target_unit / 500) * 500
        
    if res_unit > max_allowed_unit:
        # 3-қадам: 100 сўмга яхлитлаб кўрамиз
        res_unit = math.ceil(target_unit / 100) * 100
        
    if res_unit > max_allowed_unit:
        # 4-қадам (ОХИРГИ ЧОРА): 18.99% гача рухсат бериб, 100 сўмлик энг яқин нарх
        # Агар 11% ёки 18.99% оралиғида бўлса ҳам 100 сўмлик яхлитликни сақлаймиз
        res_unit = math.floor(max_allowed_unit / 100) * 100

    # Якуний пачка нархи штукка каррали бўлиши шарт!
    pachka_final = res_unit * pack_size
    dona_final = res_unit
    
    real_markup = ((pachka_final / cost) - 1) * 100 if cost > 0 else 0
    return int(pachka_final), int(dona_final), real_markup

# 2. ИНТЕРФЕЙС
st.set_page_config(page_title="MEDEXTRA PRO", layout="centered")

st.markdown("<h2 style='text-align: center; color: #004a99;'>💊 MEDEXTRA: ТОЗА НАРХЛАШ</h2>", unsafe_allow_html=True)

uploaded_files = st.file_uploader("Файлларни танланг", type=['xlsx', 'pdf'], accept_multiple_files=True)

if uploaded_files:
    try:
        # Устунларни аниқлаш
        df_sample = pd.read_excel(uploaded_files[0])
        cols = df_sample.columns.tolist()
    except:
        cols = ["Nomi", "Narxi"]
    
    c1, c2 = st.columns(2)
    col_n = c1.selectbox("💊 Дори номи", cols, index=0)
    col_c = c2.selectbox("💰 Таннарх", cols, index=min(3, len(cols)-1))

    if st.button("🚀 ҲИСОБЛАШ"):
        all_data = []
        for f in uploaded_files:
            df = pd.read_excel(f).fillna(0)
            p_res, d_res, m_res = [], [], []
            
            for _, row in df.iterrows():
                try:
                    raw_val = str(row[col_c]).replace(' ', '').replace(',', '.')
                    cost = float(re.sub(r'[^\d.]', '', raw_val))
                    size = get_pack_size(row[col_n])
                    
                    p_p, d_p, m_p = calculate_prices(cost, size)
                    
                    p_res.append(p_p)
                    d_res.append(d_p)
                    m_res.append(f"{m_p:.1f}%")
                except:
                    p_res.append(0); d_res.append(0); m_res.append("0%")
            
            df['SOTUV_PACHKA'] = p_res
            df['SOTUV_DONA'] = d_res
            df['FOYDA_FOIZ'] = m_res
            
            # Excel қилиш
            out = io.BytesIO()
            with pd.ExcelWriter(out, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            all_data.append((f.name, out.getvalue()))

        if all_data:
            if len(all_data) > 1:
                zip_b = io.BytesIO()
                with zipfile.ZipFile(zip_b, "w") as zf:
                    for name, data in all_data:
                        zf.writestr(f"Tayyor_{name}", data)
                st.download_button("📥 ZIP ЮКЛАШ", zip_b.getvalue(), "Natijalar.zip")
            else:
                st.download_button("📥 Excelни юклаш", all_data[0][1], f"Tayyor_{all_data[0][0]}")
