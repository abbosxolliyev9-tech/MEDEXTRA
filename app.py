import streamlit as st
import os

# 1. Тўғри папкалардан функцияларни чақириш
try:
    from tizim import auth # Рўйхатдан ўтиш ва кириш учун
    from calculations.logic import process_excel_files # Ҳисоб-китоб учун
except ImportError as e:
    st.error(f"❌ Файлларни топишда хатолик: {e}. GitHub-да 'tizim' ва 'calculations' папкалари мавжудлигини текширинг.")
    st.stop()

# 2. Саҳифа конфигурацияси
st.set_page_config(page_title="MEDEXTRA", layout="wide")

# 3. Орқа фон ва Стиль
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
        .blue-label {{
            background: rgba(0, 74, 153, 0.85);
            color: white;
            padding: 15px;
            border-radius: 12px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.4);
            margin-bottom: 20px;
        }}
        </style>
        """, unsafe_allow_html=True)

apply_style()

# 4. Тизимни тайёрлаш
auth.сессияни_тайёрлаш()

# 5. Кириш текшируви
if not st.session_state.get("auth"):
    auth.кириш_ойнаси()
    st.stop()

# 6. Асосий Ишчи Майдон (Киргандан кейин)
st.sidebar.markdown(f"### 👤 {st.session_state.get('user')}")
if st.sidebar.button("🚪 Чиқиш"):
    st.session_state["auth"] = False
    st.rerun()

st.markdown('<div class="blue-label"><h1>📊 MEDEXTRA - Ҳисоб-китоб тизими</h1></div>', unsafe_allow_html=True)

# 7. Excel файлларни юклаш ва қайта ишлаш қисми
files = st.file_uploader("Excel файлларни юкланг (Бир нечта мумкин)", type=['xlsx', 'xls'], accept_multiple_files=True)

if files:
    pct = st.slider("Қўшимча фоиз миқдорини белгиланг (%):", 1, 30, 12)
    
    if st.button("🚀 ҲИСОБЛАШНИ БОШЛАШ", use_container_width=True):
        with st.spinner("Файллар қайта ишланмоқда..."):
            try:
                # 'calculations/logic.py' ичидаги функция ишлатилади
                zip_data = process_excel_files(files, pct) 
                
                st.success("✅ Ҳисоблаш муваффақиятли якунланди!")
                st.download_button(
                    label="📥 Тайёр файлни юклаб олиш (ZIP)",
                    data=zip_data,
                    file_name="MEDEXTRA_Natija.zip",
                    mime="application/zip",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Ҳисоблашда хатолик: {e}")
