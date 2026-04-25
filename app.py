import streamlit as st
import pandas as pd
import os
from calculations.logic import process_excel_files

# Файлни тўғридан-тўғри импорт қилиш
try:
    import auth
except ImportError:
    # Агар файл папка ичида қолган бўлса, бу ердан қидиради
    from tizim import auth

# Сессияни тайёрлаш
auth.сессияни_тайёрлаш()

# Дизайн
st.set_page_config(page_title="MEDEXTRA", layout="wide")

# Кириш текшируви
if not st.session_state.get("auth"):
    auth.кириш_ойнаси()
    st.stop()

# Меню
rol = st.session_state.get("role", 0)
if rol == 9:
    menu = st.sidebar.radio("Бўлим:", ["🚀 Админ Ҳисоб", "📊 Фоизли Кальк", "⚙️ Панел"])
else:
    menu = st.sidebar.radio("Бўлим:", ["📊 Фоизли Кальк"])

# Иш қисми
if menu in ["🚀 Админ Ҳисоб", "📊 Фоизли Кальк"]:
    st.header(menu)
    pct = st.slider("Фоиз:", 1, 25, 12) if menu == "📊 Фоизли Кальк" else None
    files = st.file_uploader("Excel юкланг", accept_multiple_files=True)
    if files and st.button("🚀 Ҳисоблаш"):
        zip_data = process_excel_files(files, menu, "Номи", "Таннарх", pct)
        st.download_button("📥 Натижани юклаш", zip_data, "Natija.zip")

elif menu == "⚙️ Панел":
    st.header("⚙️ Бошқарув панели")
    база = auth.маълумотларни_юклаш()
    st.dataframe(база)
