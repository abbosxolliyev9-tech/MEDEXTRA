import streamlit as st
import pandas as pd
import os
from calculations.logic import process_excel_files

# Муҳим: 'тизим' папкаси номини GitHub-да 'tizim' (лотинча) деб ўзгартирган бўлишингиз шарт
try:
    from tizim import auth
except ImportError:
    st.error("❌ 'tizim' папкаси ёки 'auth.py' файли топилмади. GitHub-да папка номи лотинча эканлигини текширинг.")
    st.stop()

# 1. Саҳифа созламалари
st.set_page_config(page_title="MEDEXTRA", layout="wide", initial_sidebar_state="expanded")

# 2. Дизайн ва Орқа фон (CSS)
def apply_style():
    bg_url = "https://raw.githubusercontent.com/abbosxolliyev9-tech/MEDEXTRA/main/pexels-eren-34577902.jpg"
    st.markdown(f"""
        <style>
        /* Асосий фон */
        .stApp {{
            background: url("{bg_url}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        
        /* Кўк панел дизайни */
        .blue-panel {{
            background: rgba(0, 74, 153, 0.85);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.3);
            margin-bottom: 25px;
        }}
        
        /* Sidebar дизайни */
        section[data-testid="stSidebar"] {{
            background-color: rgba(255, 255, 255, 0.1) !important;
            backdrop-filter: blur(10px);
        }}
        </style>
        """, unsafe_allow_html=True)

apply_style()

# 3. Сессияни тайёрлаш (auth.py ичидаги функция)
auth.сессияни_тайёрлаш()

# 4. Кириш текшируви
if not st.session_state.get("auth"):
    auth.кириш_ойнаси()
    st.stop()

# 5. Меню (Sidebar)
st.sidebar.markdown(f"### 👤 {st.session_state.get('user', 'User')}")
rol = st.session_state.get("role", 0)

if rol == 9:
    menu = st.sidebar.radio("📌 Бўлимни танланг:", ["🚀 Админ Ҳисоб", "📊 Фоизли Кальк", "⚙️ Бошқарув Панели"])
else:
    menu = st.sidebar.radio("📌 Бўлимни танланг:", ["📊 Фоизли Кальк"])

if st.sidebar.button("🚪 Тизимдан чиқиш"):
    st.session_state["auth"] = False
    st.rerun()

# 6. Асосий функционал
st.markdown(f'<div class="blue-panel"><h1>{menu}</h1></div>', unsafe_allow_html=True)

if menu in ["🚀 Админ Ҳисоб", "📊 Фоизли Кальк"]:
    # Фоиз танлаш фақат оддий кальк учун
    pct = None
    if menu == "📊 Фоизли Кальк":
        pct = st.slider("Қўшимча фоиз миқдорини белгиланг:", 1, 25, 12)
    
    files = st.file_uploader("Excel файлларни юкланг (Бир нечта мумкин)", type=['xlsx', 'xls'], accept_multiple_files=True)
    
    if files:
        if st.button("🚀 Ҳисоблашни бошлаш", use_container_width=True):
            with st.spinner("Файллар қайта ишланмоқда..."):
                try:
                    # 'calculations/logic.py' ичидаги функция чақирилади
                    zip_data = process_excel_files(files, menu, "Номи", "Таннарх", pct)
                    st.success("✅ Ҳисоблаш якунланди!")
                    st.download_button(
                        label="📥 Тайёр файлни юклаб олиш (ZIP)",
                        data=zip_data,
                        file_name="MEDEXTRA_Natija.zip",
                        mime="application/zip",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Хатолик юз берди: {e}")

elif menu == "⚙️ Бошқарув Панели":
    st.subheader("👥 Фойдаланувчилар базаси (Google Sheets)")
    база = auth.маълумотларни_юклаш()
    if not база.empty:
        st.dataframe(база, use_container_width=True)
    else:
        st.warning("Маълумотларни юклаб бўлмади.")
