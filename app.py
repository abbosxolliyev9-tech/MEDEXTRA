import streamlit as st
import pandas as pd
import io
import re
from calculations.logic import get_pack_size, calculate_logic
from tizim.auth import apply_design, login_system

st.set_page_config(page_title="MEDEXTRA", layout="wide")
apply_design()

if login_system():
    st.sidebar.title("MEDEXTRA Menyu")
    choice = st.sidebar.radio("Bo'limni tanlang:", ["Admin Hisob", "Mijoz Hisob"])
    
    if st.sidebar.button("Chiqish"):
        st.session_state.logged_in = False
        st.rerun()

    st.markdown('<div class="main-block">', unsafe_allow_html=True)
    st.title(f"📊 {choice}")
    
    mode = "admin" if choice == "Admin Hisob" else "mijoz"
    uploaded_file = st.file_uploader("Excel faylni yuklang", type=['xlsx'])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        if st.button("🚀 HISOBLASH"):
            p_res, d_res = [], []
            for _, row in df.iterrows():
                try:
                    val = str(row.iloc[3]).replace(' ', '').replace(',', '.')
                    cost = float(re.sub(r'[^\d.]', '', val))
                except: cost = 0
                
                size = get_pack_size(row.iloc[0])
                p, d = calculate_logic(cost, mode=mode, pack_size=size)
                p_res.append(p)
                d_res.append(d)
            
            df['Pachka Sotuv'] = p_res
            df['Dona Narxi'] = d_res
            st.success("Bajarildi!")
            st.dataframe(df)
            
            out = io.BytesIO()
            with pd.ExcelWriter(out, engine='xlsxwriter') as wr:
                df.to_excel(wr, index=False)
            st.download_button("📥 Yuklab olish", out.getvalue(), "natija.xlsx")
    st.markdown('</div>', unsafe_allow_html=True)
