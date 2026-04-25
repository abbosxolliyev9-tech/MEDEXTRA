import streamlit as st
import pandas as pd
from calculations.logic import process_excel_files
from тизим.кириш import сессияни_тайёрлаш, кириш_ойнаси

st.set_page_config(page_title="MEDEXTRA", page_icon="💊", layout="wide")

# Орқа фонни қайтариш
def apply_bg():
    bg_url = "https://raw.githubusercontent.com/abbosxolliyev9-tech/MEDEXTRA/main/pexels-eren-34577902.jpg"
    st.markdown(f"""
        <style>
        .stApp {{ background: url("{bg_url}"); background-size: cover; background-position: center; }}
        .blue-label {{ background: rgba(0, 74, 153, 0.9); color: white; padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 20px; border: 1px solid white; }}
        [data-testid="stSidebar"] {{ background: rgba(0, 74, 153, 0.95); }}
        [data-testid="stSidebar"] * {{ color: white !important; }}
        </style>
        """, unsafe_allow_html=True)

apply_bg()
сессияни_тайёрлаш()

if not st.session_state.get("auth"):
    кириш_ойнаси()
    st.stop()

# Ичкарига киргандан кейинги қисм
st.sidebar.title("💎 MEDEXTRA")
if st.sidebar.button("🚪 Чиқиш"):
    st.session_state["auth"] = False
    st.rerun()

rol = st.session_state.get("role", 0)
m_list = ["🚀 Админ Ҳисоб", "📊 Фоизли Кальк", "⚙️ Панел"] if rol == 9 else ["📊 Фоизли Кальк"]
menu = st.sidebar.radio("Бўлим:", m_list)

if menu in ["🚀 Админ Ҳисоб", "📊 Фоизли Кальк"]:
    st.markdown(f'<div class="blue-label">{menu}</div>', unsafe_allow_html=True)
    pct = st.slider("Фоиз:", 1, 25, 12) if menu == "📊 Фоизли Кальк" else None
    
    files = st.file_uploader("Excel юкланг", type=['xlsx'], accept_multiple_files=True)
    if files:
        sample = pd.read_excel(files[0])
        cols = sample.columns.tolist()
        c1, c2 = st.columns(2)
        col_n = c1.selectbox("💊 Номи:", cols)
        col_c = c2.selectbox("💰 Таннарх:", cols, index=min(4, len(cols)-1))
        
        if st.button("🚀 ҲИСОБЛАШ"):
            with st.spinner("Ишлаяпти..."):
                zip_data = process_excel_files(files, menu, col_n, col_c, pct)
                st.success("✅ Тайёр!")
                st.download_button("📥 ЮКЛАБ ОЛИШ", data=zip_data, file_name="Natija.zip")

st.sidebar.markdown(f"👤: {st.session_state['user']}")
