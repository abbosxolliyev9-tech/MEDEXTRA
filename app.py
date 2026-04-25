import streamlit as st
import pandas as pd
import os

# 1. Папкалардан функцияларни импорт қилиш
try:
    from tizim import auth #
    from calculations.logic import process_excel_files #
except ImportError:
    st.error("❌ Хатолик: 'tizim' ёки 'calculations' папкаси топилмади.")
    st.stop()

# 2. Саҳифа конфигурацияси
st.set_page_config(page_title="MEDEXTRA", layout="wide")

# 3. Дизайн ва Орқа фон
def apply_style():
    bg_url = "https://raw.githubusercontent.com/abbosxolliyev9-tech/MEDEXTRA/main/pexels-eren-34577902.jpg"
    st.markdown(f"""
        <style>
        .stApp {{
            background: url("{bg_url}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .main-panel {{
            background: rgba(0, 74, 153, 0.85);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.3);
            margin-bottom: 25px;
        }}
        </style>
        """, unsafe_allow_html=True)

apply_style()

# 4. Тизимни ишга тушириш
auth.сессияни_тайёрлаш()

# 5. Кириш текшируви
if not st.session_state.get("auth"):
    auth.кириш_ойнаси()
    st.stop()

# 6. Ролларни аниқлаш
user_role = int(st.session_state.get("role", 0))
user_name = st.session_state.get("user", "User")

st.sidebar.markdown(f"### 👤 {user_name}")

# МЕНЮ (Админ ва Мижоз учун алоҳида)
if user_role == 9: # Админ статуси
    menu = st.sidebar.radio("📌 Бўлимни танланг:", ["🚀 Админ Ҳисоб (10%)", "📊 Мижоз Ҳисоби (Эркин %)", "⚙️ Базани бошқариш"])
else:
    menu = st.sidebar.radio("📌 Бўлимни танланг:", ["📊 Мижоз Ҳисоби (Эркин %)"])

if st.sidebar.button("🚪 Тизимдан чиқиш"):
    st.session_state["auth"] = False
    st.rerun()

# --- БЎЛИМЛАР ИШЛАШИ ---

# АДМИН БЎЛИМИ (Кечаги 10% лик ўзгармас тизим)
if menu == "🚀 Админ Ҳисоб (10%)":
    st.markdown('<div class="main-panel"><h1>🚀 Админ Махсус Ҳисоб (10%)</h1></div>', unsafe_allow_html=True)
    files = st.file_uploader("Excel файлларни юкланг:", type=['xlsx', 'xls'], accept_multiple_files=True, key="adm")
    if files:
        if st.button("🚀 АДМИН ҲИСОБНИ БОШЛАШ", use_container_width=True):
            zip_data = process_excel_files(files, 10) # 10% ўзгармас
            st.success("✅ Тайёр!")
            st.download_button("📥 Юклаб олиш", data=zip_data, file_name="Admin_10pct.zip")

# МИЖОЗ БЎЛИМИ (1% дан 20% гача танлаш)
elif menu == "📊 Мижоз Ҳисоби (Эркин %)":
    st.markdown('<div class="main-panel"><h1>📊 Мижозлар учун Ҳисоб-китоб</h1></div>', unsafe_allow_html=True)
    files = st.file_uploader("Excel файлларни юкланг:", type=['xlsx', 'xls'], accept_multiple_files=True, key="cln")
    if files:
        # Мижоз учун фоиз танлаш блоки
        client_pct = st.select_slider("Фоизни танланг:", options=list(range(1, 21)), value=12)
        if st.button("🚀 ҲИСОБЛАШ", use_container_width=True):
            zip_data = process_excel_files(files, client_pct) # Мижоз танлаган фоиз
            st.success(f"✅ {client_pct}% билан ҳисобланди!")
            st.download_button("📥 Юклаб олиш", data=zip_data, file_name=f"Mijoz_{client_pct}pct.zip")

# БАЗА (Фақат Админ кўради)
elif menu == "⚙️ Базани бошқариш":
    st.markdown('<div class="main-panel"><h1>⚙️ Фойдаланувчилар Базаси</h1></div>', unsafe_allow_html=True)
    try:
        users_data = auth.маълумотларни_юклаш() #
        st.dataframe(users_data, use_container_width=True)
    except Exception as e:
        st.error(f"Базада хатолик: {e}")
