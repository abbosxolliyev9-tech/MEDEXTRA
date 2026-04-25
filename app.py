import streamlit as st
import pandas as pd
from calculations.logic import process_excel_files
# Энди инглизча ном орқали хатосиз ишлайди
from tizim.auth import сессияни_тайёрлаш, кириш_ойнаси, маълумотларни_юклаш

st.set_page_config(page_title="MEDEXTRA", layout="wide")

# Дизайн ва сессия
сессияни_тайёрлаш()

if not st.session_state.get("auth"):
    кириш_ойнаси()
    st.stop()

# Меню
rol = st.session_state.get("role", 0)
if rol == 9:
    menu = st.sidebar.radio("Бўлим:", ["🚀 Админ Ҳисоб", "📊 Фоизли Кальк", "⚙️ Панел"])
else:
    menu = st.sidebar.radio("Бўлим:", ["📊 Фоизли Кальк"])

# Ишчи қисм
if menu == "📊 Фоизли Кальк" or menu == "🚀 Админ Ҳисоб":
    st.title(menu)
    pct = st.slider("Фоиз:", 1, 25, 12) if menu == "📊 Фоизли Кальк" else None
    files = st.file_uploader("Файлларни юкланг", accept_multiple_files=True)
    if files and st.button("Ҳисоблаш"):
        zip_data = process_excel_files(files, menu, "Номи", "Таннарх", pct)
        st.download_button("Юклаб олиш", zip_data, "Natija.zip")

elif menu == "⚙️ Панел":
    st.title("⚙️ Бошқарув панели")
    база = маълумотларни_юклаш()
    st.dataframe(база)
