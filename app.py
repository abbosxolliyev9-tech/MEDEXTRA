import streamlit as st
import pandas as pd
import os

# 1. Папкалардан функцияларни импорт қилиш
try:
    from tizim import auth 
    from calculations.logic import process_excel_files 
except ImportError:
    st.error("❌ 'tizim' ёки 'calculations' папкаси топилмади. GitHub-да номларни текширинг!")
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

# 6. МЕНЮ ВА РОЛЛАРНИ БОШҚАРИШ
# Роль 9 - бу Админ (Google Sheets-да status устунида 9 деб ёзилган бўлиши керак)
user_role = int(st.session_state.get("role", 0))
user_name = st.session_state.get("user", "Меҳмон")

st.sidebar.markdown(f"### 👤 {user_name}")

# Меню танловлари рольга қараб ўзгаради
menu_options = ["📊 Хисоб-китоб (Мижоз)"]
if user_role == 9:
    menu_options.append("⚙️ Админ Панел (База)")

choice = st.sidebar.radio("📌 Бўлимни танланг:", menu_options)

if st.sidebar.button("🚪 Тизимдан чиқиш"):
    st.session_state["auth"] = False
    st.rerun()

# --- БЎЛИМЛАРНИНГ ИШЛАШИ ---

if choice == "📊 Хисоб-китоб (Мижоз)":
    st.markdown('<div class="main-panel"><h1>📊 Excel Ҳисоб-китоб Бўлими</h1></div>', unsafe_allow_html=True)
    
    files = st.file_uploader("Excel файлларни юкланг:", type=['xlsx', 'xls'], accept_multiple_files=True)
    
    if files:
        pct = st.slider("Қўшимча фоиз миқдори (%):", 1, 30, 12)
        if st.button("🚀 ҲИСОБЛАШНИ БОШЛАШ", use_container_width=True):
            with st.spinner("Ҳисобланмоқда..."):
                try:
                    zip_data = process_excel_files(files, pct)
                    st.success("✅ Тайёр!")
                    st.download_button("📥 Натижани юклаб олиш (ZIP)", data=zip_data, file_name="Natija.zip", use_container_width=True)
                except Exception as e:
                    st.error(f"Хато: {e}")

elif choice == "⚙️ Админ Панел (База)":
    st.markdown('<div class="main-panel"><h1>⚙️ Админ Панел: Фойдаланувчилар Базаси</h1></div>', unsafe_allow_html=True)
    
    st.info("ℹ️ Бу ерда Google Sheets-даги барча рўйхатдан ўтганлар кўринади.")
    
    # Google Sheets-дан маълумотларни тортиш
    try:
        data = auth.маълумотларни_юклаш()
        if not data.empty:
            # Маълумотларни чиройли жадвал қилиб кўрсатиш
            st.dataframe(data, use_container_width=True)
            
            st.divider()
            st.subheader("📝 Янги сўровларни тасдиқлаш бўйича йўриқнома:")
            st.write("1. Янги рўйхатдан ўтганларнинг `status` устуни автоматик **0** бўлади.")
            st.write("2. Уларга рухсат бериш учун [Google Sheets](https://docs.google.com/spreadsheets/d/1XyO5EqqDonEfQnmqr8j7SQNbVcx2SC93txhFVHoDGQA/edit) файлингизга киринг.")
            st.write("3. Керакли одамнинг `status` устунини **1** (мижоз) ёки **9** (админ) қилиб ўзгартиринг.")
        else:
            st.warning("Базада маълумот топилмади.")
    except Exception as e:
        st.error(f"Базани юклашда хатолик: {e}")
