import streamlit as st
import pandas as pd

# 1. Sayt sozlamalari va Login tizimi
st.set_page_config(page_title="Narx Avtomatizatori", layout="wide")

# Oddiy xavfsizlik (Login: admin, Parol: 12345) - buni o'zgartirishingiz mumkin
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if not st.session_state.password_correct:
        st.title("Tizimga kirish")
        user = st.text_input("Login")
        pwd = st.text_input("Parol", type="password")
        if st.button("Kirish"):
            if user == "admin" and pwd == "12345": # O'zingizga yoqqanini qo'ying
                st.session_state.password_correct = True
                st.rerun()
            else:
                st.error("Login yoki parol xato!")
        return False
    return True

if check_password():
    st.sidebar.title("Sozlamalar")
    st.title("🚀 Narxlarni avtomatik shakllantirish")
    
    # 2. Ustama foizlarini belgilash
    min_pct = st.sidebar.number_input("Minimal ustama (%)", value=12.0)
    max_pct = st.sidebar.number_input("Maximal ustama (%)", value=17.0)
    
    # 3. Fayl yuklash
    uploaded_file = st.file_uploader("Excel faylni (XLSX) yuklang", type=['xlsx'])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        
        # Ustunlarni avtomatik qidirish
        st.info("Jadval yuklandi. Narx ustunini tanlang.")
        cost_col = st.selectbox("Sotib olingan narx ustuni:", df.columns)
        
        if st.button("Hisoblashni boshlash"):
            # O'rtacha foizni olish (masalan 15%)
            avg_pct = (min_pct + max_pct) / 2
            
            # Narxni hisoblash
            df['Yangi Narx'] = df[cost_col] * (1 + avg_pct / 100)
            
            # 100 so'mga yaxlitlash logikasi
            def round_to_100(x):
                return round(x / 100) * 100
            
            df['Yakuniy Sotuv Narxi'] = df['Yangi Narx'].apply(round_to_100)
            df['Ustama (%)'] = avg_pct
            df['Foyda (so\'m)'] = df['Yakuniy Sotuv Narxi'] - df[cost_col]

            st.success("Muvaffaqiyatli hisoblandi!")
            st.dataframe(df.head(10)) # Oldindan ko'rish

            # Faylni saqlash va yuklab olish
            file_name = "tayyor_narxlar.xlsx"
            df.to_excel(file_name, index=False)
            
            with open(file_name, "rb") as f:
                st.download_button(
                    label="📥 Tayyor Excel faylni yuklab olish",
                    data=f,
                    file_name="hisoblangan_narxlar.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
