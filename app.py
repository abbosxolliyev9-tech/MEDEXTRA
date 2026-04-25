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
    # GitHub'даги расм линки
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

# 6. Ролларни аниқлаш (Google Sheets-даги 'status' устуни асосида)
user_role = int(st.session_state.get("role", 0))
user_name = st.session_state.get("user", "User")

st.sidebar.markdown(f"### 👤 {user_name}")

# МЕНЮ (Админ ва Мижоз учун алоҳида танловлар)
if user_role == 9: # Админ учун
    menu = st.sidebar.radio("📌 Бўлимни танланг:", ["🚀 Админ Ҳисоб (10%)", "📊 Мижоз Ҳисоби (Эркин %)", "⚙️ Google Sheets База"])
else: # Оддий мижоз учун
    menu = st.sidebar.radio("📌 Бўлимни танланг:", ["📊 Мижоз Ҳисоби (Эркин %)"])

if st.sidebar.button("🚪 Тизимдан чиқиш"):
    st.session_state["auth"] = False
    st.rerun()

# --- БЎЛИМЛАРНИНГ ФУНКЦИОНАЛИ ---

# 1. АДМИН МАХСУС ҲИСОБИ (Кечаги 10% лик алгоритм)
if menu == "🚀 Админ Ҳисоб (10%)":
    st.markdown('<div class="main-panel"><h1>🚀 Админ Махсус Ҳисоб (10%)</h1></div>', unsafe_allow_html=True)
    files = st.file_uploader("Excel файлларни юкланг:", type=['xlsx', 'xls'], accept_multiple_files=True, key="admin_up")
    if files:
        if st.button("🚀 АДМИН ҲИСОБНИ БОШЛАШ", use_container_width=True):
            with st.spinner("Админ алгоритми ишламоқда..."):
                zip_data = process_excel_files(files, 10) # 10% ўзгармас
                st.success("✅ Админ ҳисоби якунланди!")
                st.download_button("📥 Натижани юклаб олиш (ZIP)", data=zip_data, file_name="Admin_10pct.zip", use_container_width=True)

# 2. МИЖОЗЛАР ҲИСОБИ (1% дан 20% гача танлаш имконияти)
elif menu == "📊 Мижоз Ҳисоби (Эркин %)":
    st.markdown('<div class="main-panel"><h1>📊 Мижозлар учун Ҳисоб-китоб</h1></div>', unsafe_allow_html=True)
    files = st.file_uploader("Excel файлларни юкланг:", type=['xlsx', 'xls'], accept_multiple_files=True, key="client_up")
    if files:
        # Мижоз ўзи учун фоиз танлайди
        client_pct = st.select_slider("Керакли фоизни танланг:", options=list(range(1, 21)), value=12)
        if st.button("🚀 ҲИСОБЛАШНИ БОШЛАШ", use_container_width=True):
            with st.spinner(f"{client_pct}% билан ҳисобланмоқда..."):
                zip_data = process_excel_files(files, client_pct)
                st.success(f"✅ {client_pct}% билан тайёр бўлди!")
                st.download_button("📥 Натижани юклаб олиш (ZIP)", data=zip_data, file_name=f"Mijoz_{client_pct}pct.zip", use_container_width=True)

# 3. GOOGLE SHEETS БАЗАСИ (ФАҚАТ АДМИН УЧУН)
elif menu == "⚙️ Google Sheets База":
    st.markdown('<div class="main-panel"><h1>⚙️ Google Sheets: Фойдаланувчилар Базаси</h1></div>', unsafe_allow_html=True)
    st.info("ℹ️ Бу ерда Google Sheets-даги барча рўйхатдан ўтганлар кўринади.")
    
    try:
        # Google Sheets-дан маълумотларни юклаш
        df_base = auth.маълумотларни_юклаш() 
        if not df_base.empty:
            st.dataframe(df_base, use_container_width=True) #
            st.divider()
            st.write("🔗 [Google Sheets-га ўтиш ва тасдиқлаш](https://docs.google.com/spreadsheets/d/1XyO5EqqDonEfQnmqr8j7SQNbVcx2SC93txhFVHoDGQA/edit)")
        else:
            st.warning("База бўш.")
    except Exception as e:
        st.error(f"Базани юклашда хато: {e}")
