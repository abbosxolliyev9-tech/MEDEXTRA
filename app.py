import streamlit as st
import pandas as pd

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

# 6. Ролларни аниқлаш
# Google Sheets-да status 9 бўлса Админ, 1 бўлса Мижоз
user_role = int(st.session_state.get("role", 0))
user_name = st.session_state.get("user", "User")

st.sidebar.markdown(f"### 👤 {user_name}")

# Меню шакллантириш
if user_role == 9:
    menu = st.sidebar.radio("📌 Бўлимни танланг:", ["🚀 Админ Ҳисоб (10%)", "📊 Мижоз Ҳисоби (Эркин %)", "⚙️ Базани бошқариш"])
else:
    menu = st.sidebar.radio("📌 Бўлимни танланг:", ["📊 Мижоз Ҳисоби (Эркин %)"])

if st.sidebar.button("🚪 Тизимдан чиқиш"):
    st.session_state["auth"] = False
    st.rerun()

# --- БЎЛИМЛАР МАНТИҚИ ---

# 1-БЎЛИМ: АДМИН УЧУН МАХСУС ҲИСОБ (Кечаги 10% лик тизим)
if menu == "🚀 Админ Ҳисоб (10%)":
    st.markdown('<div class="main-panel"><h1>🚀 Админ Махсус Ҳисоб-китоб (10%)</h1></div>', unsafe_allow_html=True)
    st.info("ℹ️ Бу бўлим фақат сиз учун. Ҳисоб-китоб кечаги 10% лик алгоритм асосида ишлайди.")
    
    files = st.file_uploader("Excel файлларни юкланг:", type=['xlsx', 'xls'], accept_multiple_files=True, key="admin_files")
    
    if files:
        if st.button("🚀 АДМИН ҲИСОБНИ БОШЛАШ", use_container_width=True):
            with st.spinner("Админ алгоритми ишламоқда..."):
                # Сиз учун фоиз ўзгармас 10 деб юборилади
                zip_data = process_excel_files(files, 10) 
                st.success("✅ Админ ҳисоби тайёр!")
                st.download_button("📥 Юклаб олиш (ZIP)", data=zip_data, file_name="Admin_Natija.zip", use_container_width=True)

# 2-БЎЛИМ: МИЖОЗЛАР УЧУН ЭРКИН ФОИЗЛИ ҲИСОБ
elif menu == "📊 Мижоз Ҳисоби (Эркин %)":
    st.markdown('<div class="main-panel"><h1>📊 Мижозлар учун Ҳисоб-китоб</h1></div>', unsafe_allow_html=True)
    
    files = st.file_uploader("Excel файлларни юкланг:", type=['xlsx', 'xls'], accept_multiple_files=True, key="client_files")
    
    if files:
        # Мижоз ўзи учун 1% дан 20% гача танлайди
        client_pct = st.select_slider("Ўзингизга керакли фоизни танланг:", options=list(range(1, 21)), value=12)
        
        st.write(f"🔢 Танланган фоиз: **{client_pct}%**")
        
        if st.button("🚀 ҲИСОБЛАШНИ БОШЛАШ", use_container_width=True):
            with st.spinner("Ҳисобланмоқда..."):
                try:
                    # Мижоз танлаган фоиз юборилади
                    zip_data = process_excel_files(files, client_pct)
                    st.success(f"✅ {client_pct}% билан ҳисобланди!")
                    st.download_button("📥 Натижани юклаб олиш (ZIP)", data=zip_data, file_name=f"Mijoz_{client_pct}pct.zip", use_container_width=True)
                except Exception as e:
                    st.error(f"Хатолик: {e}")

# 3-БЎЛИМ: БАЗАНИ КЎРИШ (ФАҚАТ АДМИНГА)
elif menu == "⚙️ Базани бошқариш":
    st.markdown('<div class="main-panel"><h1>⚙️ Фойдаланувчилар Базаси</h1></div>', unsafe_allow_html=True)
    try:
        ba`za = auth.маълумотларни_юклаш() #
        st.dataframe(ba`za, use_container_width=True)
    except:
        st.error("Базага боғланишда хатолик.")
