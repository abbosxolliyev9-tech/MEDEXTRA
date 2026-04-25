import streamlit as st
import pandas as pd
import io
import re

# Boshqa fayllardan funksiyalarni import qilish
from calculations.logic import get_pack_size, calculate_logic
from tizim.auth import apply_design, login_system

# 1. Sahifa sozlamalari
st.set_page_config(page_title="MEDEXTRA", layout="wide")

# 2. Dizaynni qo'llash
apply_design()

# 3. Loginni tekshirish
if login_system():
    # Sidebar menyusi
    st.sidebar.title("Menyu")
    choice = st.sidebar.radio("Bo'limni tanlang:", ["Admin Hisob", "Mijoz Hisob"])
    
    if st.sidebar.button("Chiqish"):
        st.session_state.logged_in = False
        st.rerun()

    # Asosiy blok
    st.markdown('<div class="main-block">', unsafe_allow_html=True)
    st.title(f"📊 {choice}")
    
    mode = "admin" if choice == "Admin Hisob" else "mijoz"
    user_markup = 10
    if mode == "mijoz":
        user_markup = st.select_slider("Ustama foizini tanlang (%):", options=list(range(1, 21)), value=10)

    # Fayl yuklash
    uploaded_file = st.file_uploader("Excel faylni tanlang (xlsx)", type=['xlsx'])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        cols = df.columns.tolist()
        
        c1, c2 = st.columns(2)
        with c1: col_name = st.selectbox("Dori nomi ustuni:", cols, index=0)
        with c2: col_cost = st.selectbox("Tannarx ustuni:", cols, index=min(3, len(cols)-1))
        
        if st.button("🚀 HISOBLASHNI BOSHLASH"):
            p_res, d_res = [], []
            for _, row in df.iterrows():
                try:
                    # Narxdagi bo'shliqlarni tozalash
                    raw_val = str(row[col_cost]).replace(' ', '').replace(',', '.')
                    cost = float(re.sub(r'[^\d.]', '', raw_val))
                except:
                    cost = 0
                
                size = get_pack_size(row[col_name])
                p_val, d_val = calculate_logic(cost, mode=mode, user_markup=user_markup, pack_size=size)
                
                p_res.append(p_val)
                d_res.append(d_val)
            
            df['Pachka Sotuv (Yangi)'] = p_res
            df['Dona Narxi (Yangi)'] = d_res
            
            st.success("Muvaffaqiyatli hisoblandi!")
            st.dataframe(df.head(20)) # Oldindan ko'rish
            
            # Excel qilib saqlash
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            
            st.download_button(
                label="📥 Natijani yuklab olish",
                data=output.getvalue(),
                file_name=f"medextra_{choice.lower().replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    st.markdown('</div>', unsafe_allow_html=True)
