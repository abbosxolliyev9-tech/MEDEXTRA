import streamlit as st
import pandas as pd
from calculations.logic import process_excel_files # Фақат асосий функцияни чақирамиз
from тизим.кириш import сессияни_тайёрлаш, чиқиш_тугмаси, кириш_ойнаси

st.set_page_config(page_title="MEDEXTRA", page_icon="💊", layout="wide")
# ... (add_custom_style функцияси шу ерда қолади) ...

сессияни_тайёрлаш()
if not st.session_state.get("auth"):
    кириш_ойнаси()
    st.stop()

чиқиш_тугмаси()
rol = st.session_state.get("role", 0)
menu = st.sidebar.radio("Бўлим:", ["🚀 Админ Ҳисоб", "📊 Фоизли Кальк", "⚙️ Панел"] if rol == 9 else ["📊 Фоизли Кальк"])

if menu in ["🚀 Админ Ҳисоб", "📊 Фоизли Кальк"]:
    st.markdown(f'<div class="blue-label">{menu}</div>', unsafe_allow_html=True)
    user_pct = st.slider("Фоиз:", 1, 25, 12) if menu == "📊 Фоизли Кальк" else None
    
    files = st.file_uploader("Excel юкланг", type=['xlsx'], accept_multiple_files=True)
    if files:
        sample_df = pd.read_excel(files[0])
        cols = sample_df.columns.tolist()
        c1, c2 = st.columns(2)
        col_n = c1.selectbox("💊 Номи:", cols)
        col_c = c2.selectbox("💰 Таннарх:", cols, index=min(4, len(cols)-1))
        
        if st.button("🚀 ҲИСОБЛАШ"):
            # Ҳамма оғир иш "calculations/logic.py" ичида бажарилади
            zip_data = process_excel_files(files, menu, col_n, col_c, user_pct)
            st.success("✅ Тайёр!")
            st.download_button("📥 ЮКЛАБ ОЛИШ", data=zip_data, file_name="Natija.zip")
