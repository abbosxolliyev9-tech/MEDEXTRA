import streamlit as st
import pandas as pd
import io
import re
from calculations.logic import get_pack_size, calculate_logic
from tizim.auth import apply_design, login_system

st.set_page_config(page_title="MEDEXTRA", layout="wide")
apply_design()

if login_system():
    st.sidebar.title(f"Xush kelibsiz!")
    menu = ["Admin Hisob-kitob", "Mijoz Hisob-kitob"]
    choice = st.sidebar.selectbox("Bo'limni tanlang", menu)
    
    if st.sidebar.button("Chiqish"):
        st.session_state.logged_in = False
        st.rerun()

    st.markdown('<div class="main-block">', unsafe_allow_html=True)
    st.title(f"📊 {choice}")
    
    mode = "admin" if choice == "Admin Hisob-kitob" else "mijoz"
    user_markup = 10
    if mode == "mijoz":
        user_markup = st.select_slider("Ustama foizini tanlang (%):", options=list(range(1, 21)), value=10)

    uploaded_file = st.file_uploader("Excel faylni yuklang", type=['xlsx'])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        cols = df.columns.tolist()
        
        c1, c2 = st.columns(2)
        with c1: col_name = st.selectbox("Dori nomi ustuni:", cols, index=0)
        with c2: col_cost = st.selectbox("Tannarx ustuni:", cols, index=3 if len(cols)>3 else 0)
        
        if st.button("🚀 HISOBLASHNI BOSHLASH"):
            p_res, d_res = [], []
            for _, row in df.iterrows():
                try:
                    raw_val = str(row[col_cost]).replace(' ', '').replace(',', '.')
                    cost = float(re.sub(r'[^\d.]', '', raw_val))
                except: cost = 0
                
                size = get_pack_size(row[col_name])
                p_val, d_val = calculate_logic(cost, mode=mode, user_markup=user_markup, pack_size=size)
                p_res.append(p_val)
                d_res.append(d_val)
            
            df['Pachka Sotuv'] = p_res
            df['Dona Narxi'] = d_res
            st.success("Hisoblandi!")
            st.dataframe(df)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            st.download_button("📥 Yuklab olish", output.getvalue(), "natija.xlsx")
    st.markdown('</div>', unsafe_allow_html=True)
