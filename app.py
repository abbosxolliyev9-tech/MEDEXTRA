import streamlit as st
import pandas as pd
import io
import re

# Papkalardan import qilish
from calculations.logic import get_pack_size, calculate_logic
from tizim.auth import apply_design, login_system

st.set_page_config(page_title="MEDEXTRA", layout="wide")
apply_design()

if login_system():
    st.sidebar.title("MEDEXTRA")
    choice = st.sidebar.radio("Bo'lim:", ["Admin Hisob", "Mijoz Hisob"])
    
    st.markdown('<div class="main-block">', unsafe_allow_html=True)
    st.title(f"📊 {choice}")
    
    uploaded_file = st.file_uploader("Excel yuklang", type=['xlsx'])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        if st.button("🚀 Hisoblash"):
            p_res, d_res = [], []
            for _, row in df.iterrows():
                try:
                    # Narxdan hamma harflarni olib tashlash, faqat raqam qoldirish
                    val = re.sub(r'[^\d.]', '', str(row.iloc[3]))
                    cost = float(val) if val else 0
                except: cost = 0
                
                size = get_pack_size(row.iloc[0])
                p, d = calculate_logic(cost, mode="admin" if "Admin" in choice else "mijoz", pack_size=size)
                p_res.append(p)
                d_res.append(d)
            
            df['Pachka Sotuv'] = p_res
            df['Dona Sotuv'] = d_res
            st.dataframe(df)
            
            out = io.BytesIO()
            with pd.ExcelWriter(out, engine='xlsxwriter') as wr:
                df.to_excel(wr, index=False)
            st.download_button("📥 Yuklab olish", out.getvalue(), "natija.xlsx")
    st.markdown('</div>', unsafe_allow_html=True)
