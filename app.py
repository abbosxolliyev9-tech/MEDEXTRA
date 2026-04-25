import streamlit as st
import pandas as pd
import io
import re
import math

st.set_page_config(page_title="MEDEXTRA | Professional", layout="wide")
st.title("💊 MEDEXTRA: Aqlli Hisob-Kitob Tizimi")

def get_pack_size(name):
    """Dori nomidan №8, №10 kabi dona sonini topish"""
    name_str = str(name).upper()
    match = re.search(r'[N№](\d+)', name_str)
    return int(match.group(1)) if match else 1

def calculate_logic(cost):
    """Siz aytgan formula: 12% ustama va 100 ga tepaga yaxlitlash"""
    if cost <= 0: return 0
    # 1. Pachka narxi: Tannarx + 12% va tepaga 100 ga yaxlitlash
    pachka_final = math.ceil((cost * 1.12) / 100) * 100
    return pachka_final

# Faylni yuklash
uploaded_files = st.file_uploader("Excel fayllarni yuklang", type=['xlsx'], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        try:
            df = pd.read_excel(uploaded_file)
            cols = df.columns.tolist()
            
            st.write(f"📁 Fayl: {uploaded_file.name}")
            col_name = st.selectbox(f"Dori nomi (A) - {uploaded_file.name}:", cols, index=0)
            col_cost = st.selectbox(f"Tannarx (D) - {uploaded_file.name}:", cols, index=3 if len(cols)>3 else 0)
            
            if st.button(f"🚀 Hisoblash: {uploaded_file.name}"):
                p_list, d_list = [], []
                
                for _, row in df.iterrows():
                    try:
                        # Narxni tozalash
                        raw_v = str(row[col_cost]).replace(' ', '').replace(',', '.')
                        cost = float(re.sub(r'[^\d.]', '', raw_v))
                    except: cost = 0
                    
                    # 1. Pachka narxini hisoblash (77245 -> 86600)
                    p_price = calculate_logic(cost)
                    
                    # 2. Dona narxini hisoblash (86600 / 8 = 10825 -> 10900)
                    size = get_pack_size(row[col_name])
                    d_price = math.ceil((p_price / size) / 100) * 100
                    
                    p_list.append(p_price)
                    d_list.append(d_price)
                
                df['Pachka Sotuv (H)'] = p_list
                df['Dona Narxi (I)'] = d_list
                
                st.dataframe(df)
                
                # Yuklab olish uchun fayl tayyorlash
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False)
                st.download_button(f"📥 {uploaded_file.name} natijasini yuklab olish", output.getvalue(), f"tayyor_{uploaded_file.name}")
                
        except Exception as e:
            st.error(f"Faylni o'qishda xato: {e}")
