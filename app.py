import streamlit as st
import pandas as pd
import io
import re
import math
import hashlib
import zipfile
from calculations.logic import admin_calculate, user_calculate, get_pack_size
from тизим.кириш import сессияни_тайёрлаш, чиқиш_тугмаси, кириш_ойнаси

# --- САҲИФА СОЗЛАМАЛАРИ ---
st.set_page_config(page_title="MEDEXTRA", page_icon="💊", layout="wide")

# --- ДИЗАЙН ---
def add_custom_style():
    bg_image = "https://raw.githubusercontent.com/abbosxolliyev9-tech/MEDEXTRA/main/pexels-eren-34577902.jpg"
    st.markdown(f"""
        <style>
        .stApp {{ background-image: url("{bg_image}"); background-size: cover; background-position: center; }}
        .blue-label {{ background-color: #004a99; color: white !important; padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 20px; margin-bottom: 20px; border: 1px solid white; }}
        .contact-box {{ background-color: rgba(0, 74, 153, 0.85); color: white; padding: 12px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 16px; margin-top: 25px; border: 2px solid white; }}
        .stButton>button {{ background-color: #004a99 !important; color: white !important; width: 100%; font-weight: bold; border-radius: 8px; height: 45px; border: 1px solid white; }}
        [data-testid="stSidebar"] {{ background-color: rgba(0, 74, 153, 0.95); min-width: 250px !important; }}
        [data-testid="stSidebar"] * {{ color: white !important; }}
        </style>
        """, unsafe_allow_html=True)

add_custom_style()
сессияни_тайёрлаш()

# --- ЛОГИН ТЕКШИРУВИ ---
if not st.session_state.get("auth"):
    кириш_ойнаси()
    st.stop()

# --- SIDEBAR ВА МЕНЮ ---
чиқиш_тугмаси()
st.sidebar.title("💎 MEDEXTRA")

# Роль 9 бўлса Админ Ҳисоб кўринади, бўлмаса фақат Фоизли Кальк
foydalanuvchi_roli = st.session_state.get("role", 0)

if foydalanuvchi_roli == 9:
    menu = st.sidebar.radio("Бўлим танланг:", ["🚀 Админ Ҳисоб", "📊 Фоизли Кальк", "⚙️ Панел"])
else:
    menu = st.sidebar.radio("Бўлим танланг:", ["📊 Фоизли Кальк"])

# --- ИШЧИ ҚИСМ ---
if menu in ["🚀 Админ Ҳисоб", "📊 Фоизли Кальк"]:
    title = "АДМИН ҲИСОБЛАШ (Кечаги мантиқ)" if menu == "🚀 Админ Ҳисоб" else "ИХТИЁРИЙ ФОИЗЛИ ҲИСОБЛАШ"
    st.markdown(f'<div class="blue-label">{title}</div>', unsafe_allow_html=True)
    
    if menu == "📊 Фоизли Кальк":
        user_pct = st.slider("Устама фоизини танланг:", 1, 25, 12)
    
    uploaded_files = st.file_uploader("Excel файлларни юкланг", type=['xlsx'], accept_multiple_files=True)
    
    if uploaded_files:
        sample_df = pd.read_excel(uploaded_files[0])
        cols = sample_df.columns.tolist()
        c1, c2 = st.columns(2)
        col_n = c1.selectbox("💊 Номи устуни:", cols, index=0)
        col_c = c2.selectbox("💰 Таннарх устуни:", cols, index=min(4, len(cols)-1))
        
        if st.button("🚀 ҲИСОБЛАШНИ БОШЛАШ"):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for f in uploaded_files:
                    df = pd.read_excel(f)
                    p_l, d_l = [], []
                    for _, row in df.iterrows():
                        try:
                            cost = float(re.sub(r'[^\d.]', '', str(row[col_c]).replace(',','.')))
                            pack = get_pack_size(row[col_n])
                            if menu == "🚀 Админ Ҳисоб":
                                p_f, d_f = admin_calculate(cost, pack)
                            else:
                                p_f, d_f = user_calculate(cost, pack, user_pct)
                            p_l.append(p_f); d_l.append(d_f)
                        except:
                            p_l.append(0); d_l.append(0)
                    
                    df['Sotuv_Pachka'] = p_l
                    df['Sotuv_Dona'] = d_l
                    
                    excel_out = io.BytesIO()
                    with pd.ExcelWriter(excel_out, engine='xlsxwriter') as wr:
                        df.to_excel(wr, index=False)
                    zf.writestr(f"Tayyor_{f.name}", excel_out.getvalue())
            
            st.success("✅ Ҳисоблаш якунланди!")
            st.download_button("📥 НАТИЖАЛАРНИ ЮКЛАБ ОЛИШ (ZIP)", data=zip_buffer.getvalue(), file_name="MedExtra_Natija.zip")

elif menu == "⚙️ Панел":
    st.markdown('<div class="blue-label">⚙️ БОШҚАРУВ ПАНЕЛИ</div>', unsafe_allow_html=True)
    st.write("Бу ердан базани бошқаришингиз мумкин.")
