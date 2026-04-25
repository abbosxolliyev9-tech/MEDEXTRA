import streamlit as st
import pandas as pd
import io
import re

# Boshqa fayllardan funksiyalarni chaqirish
from calculations.logic import get_pack_size, calculate_logic
from tizim.auth import apply_design, login_system

# Sahifa sozlamalari
st.set_page_config(page_title="MEDEXTRA", layout="wide")

# Dizaynni qo'llash
apply_design()

# Loginni tekshirish
if login_system():
    st.sidebar.title("MEDEXTRA")
    choice = st.sidebar.radio("Bo'limni tanlang:", ["Admin Hisob", "Mijoz Hisob"])
    
    if st.sidebar.button("Tizimdan chiqish"):
        st.session_state.logged_in = False
        st.rerun()

    st.markdown('<div class="main-block">', unsafe_allow_html=True)
    st.title(f"📊 {choice}")
    
    mode = "admin" if choice == "Admin Hisob" else "mijoz"
    user_markup = 10
    if mode == "mijoz":
        user_markup = st.slider("Mijoz ustama foizi (%):", 1, 25, 10)

    # Excel yuklash
    uploaded_file = st.file_uploader("Xarid ro'yxatini yuklang (.xlsx)", type=['xlsx'])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        
        if st.button("🚀 NARXLARNI HISOBLASH"):
            p_res, d_res = [], []
            for index, row in df.iterrows():
                try:
                    # 4-ustundagi narxni olish (iloc[3])
                    val = str(row.iloc[3]).replace(' ', '').replace(',', '.')
                    cost = float(re.sub(r'[^\d.]', '', val))
                except:
                    cost = 0
                
                # 1-ustundagi nomdan dori sonini olish (iloc[0])
                size = get_pack_size(row.iloc[0])
                
                p, d = calculate_logic(cost, mode=mode, user_markup=user_markup, pack_size=size)
                p_res.append(p)
                d_res.append(d)
            
            df['Pachka Narxi'] = p_res
            df['Dona Narxi'] = d_res
            
            st.success("Hisob-kitob yakunlandi!")
            st.dataframe(df)
            
            # Excel qilib saqlash
            out = io.BytesIO()
            with pd.ExcelWriter(out, engine='xlsxwriter') as wr:
                df.to_excel(wr, index=False)
            
            st.download_button(
                label="📥 Tayyor faylni yuklab olish",
                data=out.getvalue(),
                file_name="medextra_hisob.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    st.markdown('</div>', unsafe_allow_html=True)
