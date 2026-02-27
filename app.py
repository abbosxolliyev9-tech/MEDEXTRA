import streamlit as st
import pandas as pd
import io
import re
import math

st.set_page_config(page_title="MEDEXTRA | Final System", layout="wide")
st.title("💊 MEDEXTRA: Professional Hisob-Kitob")

def get_pack_size(name):
    """Dori nomidan №8, №10 kabi sonni topish"""
    match = re.search(r'[N№](\d+)', str(name).upper())
    return int(match.group(1)) if match else 1

def calculate_prices(cost, pack_size):
    """Pachka va dona narxini hisoblash"""
    # 1. Pachka narxi: Tannarx + 12% va 100 ga tepaga yaxlitlash
    pachka_raw = cost * 1.12
    pachka_final = math.ceil(pachka_raw / 100) * 100
    
    # 2. Dona narxi: Pachka narxi / dona soni va 100 ga tepaga yaxlitlash
    # Masalan: 86600 / 8 = 10825 -> 10900
    dona_raw = pachka_final / pack_size
    dona_final = math.ceil(dona_raw / 100) * 100
    
    return pachka_final, dona_final

uploaded_file = st.file_uploader("Excel faylni yuklang", type=['xlsx'])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    cols = df.columns.tolist()
    
    col_name = st.selectbox("Dori nomi (A):", cols, index=0)
    col_cost = st.selectbox("Tannarx (D):", cols, index=3 if len(cols)>3 else 0)
    
    if st.button("🚀 Formulani ishga tushirish"):
        pachka_list, dona_list = [], []
        
        for _, row in df.iterrows():
            try:
                val = str(row[col_cost]).replace(' ', '').replace(',', '.')
                cost = float(re.sub(r'[^\d.]', '', val))
            except: cost = 0
            
            size = get_pack_size(row[col_name])
            p_price, d_price = calculate_prices(cost, size)
            
            pachka_list.append(p_price)
            dona_list.append(d_price)
            
        df['Pachka Sotuv (H)'] = pachka_list
        df['Dona Narxi (I)'] = dona_list
        
        st.success("Tayyor! 86 600 va 10 900 kabi chiroyli narxlar hisoblandi.")
        st.dataframe(df)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        st.download_button("📥 Faylni yuklab olish", output.getvalue(), "medextra_hisobot.xlsx")
