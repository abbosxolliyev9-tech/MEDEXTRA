import streamlit as st
import pandas as pd
import os
from calculations.logic import process_excel_files

# КИРИЛЛЧА ПАПКАДАН ИМПОРТ ҚИЛИШДА ХАТОЛИКНИ ОЛДИНИ ОЛИШ
import importlib.util
import sys

# 'тизим/кириш.py' файлини қўлда юклаб олиш (ImportError ни ечими)
file_path = os.path.join("тизим", "кириш.py")
spec = importlib.util.spec_from_file_location("кириш", file_path)
auth_module = importlib.util.module_from_spec(spec)
sys.modules["кириш"] = auth_module
spec.loader.exec_module(auth_module)

# Энди функцияларни ишлатсак бўлади
from кириш import сессияни_тайёрлаш, кириш_ойнаси, маълумотларни_юклаш

# 1. Саҳифа созламалари
st.set_page_config(page_title="MEDEXTRA", page_icon="💊", layout="wide")

# 2. Дизайн ва Орқа фон
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
        .blue-label {{
            background: rgba(0, 74, 153, 0.9);
            color: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
            border: 1px solid white;
            margin-bottom: 20px;
        }}
        [data-testid="stSidebar"] {{
            background: rgba(0, 74, 153, 0.95) !important;
        }}
        [data-testid="stSidebar"] * {{
            color: white !important;
        }}
        </style>
        """, unsafe_allow_html=True)

apply_style()
сессияни_тайёрлаш()

# 3. Кириш текшируви
if not st.session_state.get("auth"):
    кириш_ойнаси()
    st.stop()

# 4. Меню (Sidebar)
st.sidebar.title("💎 MEDEXTRA")
rol = st.session_state.get("role", 0)

# Ролга қараб меню чиқариш
if rol == 9:
    menu = st.sidebar.radio("Бўлим:", ["🚀 Админ Ҳисоб", "📊 Фоизли Кальк", "⚙️ Панел"])
else:
    menu = st.sidebar.radio("Бўлим:", ["📊 Фоизли Кальк"])

st.sidebar.markdown("---")
st.sidebar.write(f"👤: **{st.session_state['user']}**")
if st.sidebar.button("🚪 Чиқиш"):
    st.session_state["auth"] = False
    st.rerun()

# 5. Ишчи бўлимлар
if menu in ["🚀 Админ Ҳисоб", "📊 Фоизли Кальк"]:
    st.markdown(f'<div class="blue-label">{menu.upper()}</div>', unsafe_allow_html=True)
    
    pct = st.slider("Устама фоизи:", 1, 25, 12) if menu == "📊 Фоизли Кальк" else None
    
    files = st.file_uploader("Excel файлларни юкланг", type=['xlsx'], accept_multiple_files=True)
    if files:
        df_temp = pd.read_excel(files[0])
        cols = df_temp.columns.tolist()
        c1, c2 = st.columns(2)
        col_n = c1.selectbox("💊 Номи устуни:", cols)
        col_c = c2.selectbox("💰 Таннарх устуни:", cols, index=min(4, len(cols)-1))
        
        if st.button("🚀 ҲИСОБЛАШНИ БОШЛАШ", use_container_width=True):
            with st.spinner("Қайта ишлаш..."):
                zip_data = process_excel_files(files, menu, col_n, col_c, pct)
                st.success("✅ Тайёр!")
                st.download_button("📥 НАТИЖАНИ ЮКЛАШ (ZIP)", data=zip_data, file_name="Natija.zip", use_container_width=True)

elif menu == "⚙️ Панел":
    st.markdown('<div class="blue-label">⚙️ БОШҚАРУВ ПАНЕЛИ</div>', unsafe_allow_html=True)
    st.link_button("📂 Google Sheets Очиш", "https://docs.google.com/spreadsheets/d/1XyO5EqqDonEfQnmqr8j7SQNbVcx2SC93txhFVHoDGQA/edit", use_container_width=True)
    
    база = маълумотларни_юклаш()
    if not база.empty:
        st.subheader("👥 Фойдаланувчилар базаси")
        st.dataframe(база, use_container_width=True)
        
        # Янги сўровларни тасдиқлаш механизми
        s_col = 'status' if 'status' in база.columns else база.columns[-1]
        янгилар = база[база[s_col].astype(int) == 0]
        if not янгилар.empty:
            st.warning(f"🔔 Сизда {len(янгилар)} та янги тасдиқланмаган сўров бор!")
    else:
        st.error("Маълумотлар базаси юкланмади.")

# Пастки қисм
st.markdown('<div style="text-align: center; color: white; margin-top: 50px; opacity: 0.7;">📞 +998 88 754 98 96</div>', unsafe_allow_html=True)
