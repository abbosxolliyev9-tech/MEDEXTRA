import streamlit as st
import pandas as pd
import io
import re
import math

st.set_page_config(page_title="MEDEXTRA", layout="wide")
st.title("💊 MEDEXTRA: Aqlli Narx Tizimi")

def get_pack_size(name):
    """Dori nomidan faqat № yoki N dan keyingi dona sonini topish"""
    name_str = str(name).upper()
    # № yoki N harfidan keyin kelgan raqamlarni qidiramiz
    match = re.search(r'[N№](\d+)', name_str)
    if match:
        return int(match.group(1))
    return 1 # Agar N yo'q bo'lsa, dori 1 dona deb hisoblanadi

def find_smart_price(base_price, pack_size):
    unit_cost = base_price / (pack_size if pack_size > 0 else 1)
    
    # 1. 12% dan 18% gacha chiroyli narx qidirish
    for p in range(120, 181):
        pct = p / 10.0
        sale_price = unit_cost * (1 + pct / 100)
        if round(sale_price, 2) % 100 == 0:
            return pct, int(sale_price)
            
    # 2. Topilmasa, 12% qo'shib TEPAGA 100 ga yaxlitlash
    final_price = math.ceil((unit_cost * 1.12) / 100) * 100
    return 12.0, int(final_price)

uploaded_file = st.file_uploader("Excel (.xlsx) yuklang", type=['xlsx'])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    cols = df.columns.tolist()
    col_a = st.selectbox("Dori nomi (A):", cols, index=0)
    col_d = st.selectbox("Tannarx (D):", cols, index=3 if len(cols)>3 else 0)
    
    if st.button("🚀 Hisoblash"):
        p_list, h_list, i_list = [], [], []
        for _, row in df.iterrows():
            try:
                raw_p = str(row[col_d]).replace(' ', '').replace(',', '.')
                price = float(re.sub(r'[^\d.]', '', raw_p))
            except: price = 0
            
            size = get_pack_size(row[col_a])
            pct, unit_p = find_smart_price(price, size)
            
            p_list.append(pct)
            i_list.append(unit_p)
            h_list.append(unit_p * size)
        
        df['Ustama % (G)'] = p_list
        df['Jami Sotuv (H)'] = h_list
        df['Dona Narxi (I)'] = i_list
        st.dataframe(df)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        st.download_button("📥 Yuklab olish", output.getvalue(), "medextra_tayyor.xlsx")
