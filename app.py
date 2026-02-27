import streamlit as st
import pandas as pd
import io
import re
import math

# 1. Саҳифа созламалари
st.set_page_config(page_title="MEDEXTRA | Professional", page_icon="💊", layout="wide")

# 2. Логин тизими
def check_password():
    def password_entered():
        if st.session_state["password"] == "admin123" and st.session_state["user"] == "admin":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["user"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Логин ойнасида марказий логотип
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            st.image("https://cdn-icons-png.flaticon.com/512/3022/3022410.png", width=150) # Логотип расми
            st.markdown("<h2 style='text-align: center; color: #004a99;'>MEDEXTRA КИРИШ</h2>", unsafe_allow_html=True)
            st.text_input("Логин", key="user")
            st.text_input("Парол", type="password", key="password")
            st.button("Кириш", use_container_width=True, on_click=password_entered)
        return False
    return True

if check_password():
    # Асосий саҳифа тепасига расм қўшиш
    st.image("https://img.freepik.com/free-vector/abstract-medical-wallpaper-template-design_53876-61802.jpg", use_container_width=True) # Banner расми

    st.markdown("<h1 style='color: #004a99;'>💊 MEDEXTRA: Aqlli Narx Tizimi</h1>", unsafe_allow_html=True)
    
    # Ён панелдаги логотип
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/822/822118.png", width=80)
        st.markdown("### Ишчи панель")
        if st.button("🚪 Чиқиш"):
            st.session_state.clear()
            st.rerun()

    # Формула қисми (ўзгаришсиз)
    def get_pack_size(name):
        match = re.search(r'[N№](\d+)', str(name).upper())
        return int(match.group(1)) if match else 1

    def calculate_prices(cost, pack_size):
        pachka_final = math.ceil((cost * 1.12) / 100) * 100
        dona_final = math.ceil((pachka_final / (pack_size if pack_size > 0 else 1)) / 100) * 100
        return pachka_final, dona_final

    # Юклаш ойнаси
    st.info("📊 Илтимос, ҳисоблаш учун Excel файлини юкланг")
    uploaded_file = st.file_uploader("", type=['xlsx'])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        cols = df.columns.tolist()
        
        c1, c2 = st.columns(2)
        with c1:
            col_name = st.selectbox("Dori nomi (A):", cols, index=0)
        with c2:
            col_cost = st.selectbox("Tannarx (D):", cols, index=3 if len(cols)>3 else 0)
        
        if st.button("🚀 ХИСОБЛАШ", use_container_width=True):
            # Бу ерда ҳисоблаш мантиғи (юқоридагидек қолади)
            p_list, d_list = [], []
            for _, row in df.iterrows():
                try:
                    val = str(row[col_cost]).replace(' ', '').replace(',', '.')
                    cost = float(re.sub(r'[^\d.]', '', val))
                except: cost = 0
                size = get_pack_size(row[col_name])
                p_p, d_p = calculate_prices(cost, size)
                p_list.append(p_p)
                d_list.append(d_p)
            
            df['Pachka Sotuv (H)'] = p_list
            df['Dona Narxi (I)'] = d_list
            
            st.success("✅ Тайёр!")
            st.dataframe(df)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            st.download_button("📥 НАТИЖАНИ ЮКЛАБ ОЛИШ", output.getvalue(), "medextra_final.xlsx", use_container_width=True)
