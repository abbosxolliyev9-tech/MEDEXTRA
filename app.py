import streamlit as st
import pandas as pd
from calculations.logic import process_excel_files
from тизим.кириш import сессияни_тайёрлаш, кириш_ойнаси, маълумотларни_юклаш

# 1. Саҳифа созламалари
st.set_page_config(page_title="MEDEXTRA", page_icon="💊", layout="wide")

# 2. Дизайн ва Орқа фон
def apply_style():
    bg_url = "https://raw.githubusercontent.com/abbosxolliyev9-tech/MEDEXTRA/main/pexels-eren-34577902.jpg"
    st.markdown(f"""
        <style>
        .stApp {{ background: url("{bg_url}"); background-size: cover; background-position: center; background-attachment: fixed; }}
        .blue-label {{ background: rgba(0, 74, 153, 0.9); color: white; padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; border: 1px solid white; margin-bottom: 20px; }}
        [data-testid="stSidebar"] {{ background: rgba(0, 74, 153, 0.95) !important; }}
        [data-testid="stSidebar"] * {{ color: white !important; }}
        .stTabs [data-baseweb="tab-list"] {{ background-color: rgba(255,255,255,0.1); border-radius: 10px; }}
        </style>
        """, unsafe_allow_html=True)

apply_style()
сессияни_тайёрлаш()

# 3. Кириш текшируви
if not st.session_state.get("auth"):
    кириш_ойнаси()
    st.stop()

# 4. Sidebar (Меню)
st.sidebar.title("💎 MEDEXTRA")
rol = st.session_state.get("role", 0)

# Меню тузилиши
if rol == 9:
    menu = st.sidebar.radio("Бўлим:", ["🚀 Админ Ҳисоб", "📊 Фоизли Кальк", "⚙️ Панел"])
else:
    menu = st.sidebar.radio("Бўлим:", ["📊 Фоизли Кальк"])

st.sidebar.markdown("---")
st.sidebar.write(f"👤: **{st.session_state['user']}**")
if st.sidebar.button("🚪 Чиқиш"):
    st.session_state["auth"] = False
    st.rerun()

# 5. Асосий ишчи бўлимлар
if menu == "🚀 Админ Ҳисоб" or menu == "📊 Фоизли Кальк":
    st.markdown(f'<div class="blue-label">{menu}</div>', unsafe_allow_html=True)
    pct = st.slider("Устама фоизи:", 1, 25, 12) if menu == "📊 Фоизли Кальк" else None
    
    files = st.file_uploader("Excel файлларни танланг", type=['xlsx'], accept_multiple_files=True)
    if files:
        df_temp = pd.read_excel(files[0])
        cols = df_temp.columns.tolist()
        c1, c2 = st.columns(2)
        col_n = c1.selectbox("💊 Номи устуни:", cols)
        col_c = c2.selectbox("💰 Таннарх устуни:", cols, index=min(4, len(cols)-1))
        
        if st.button("🚀 ҲИСОБЛАШНИ БОШЛАШ", use_container_width=True):
            with st.spinner("Файллар қайта ишланмоқда..."):
                zip_data = process_excel_files(files, menu, col_n, col_c, pct)
                st.success("✅ Ҳисоблаш якунланди!")
                st.download_button("📥 НАТИЖАНИ ЮКЛАШ (ZIP)", data=zip_data, file_name="MedExtra_Natija.zip", use_container_width=True)

elif menu == "⚙️ Панел":
    st.markdown('<div class="blue-label">⚙️ БОШҚАРУВ ПАНЕЛИ</div>', unsafe_allow_html=True)
    
    # Google Sheets тугмаси
    sheet_url = "https://docs.google.com/spreadsheets/d/1XyO5EqqDonEfQnmqr8j7SQNbVcx2SC93txhFVHoDGQA/edit"
    st.link_button("📂 Google Sheets Базасини Очиш", sheet_url, use_container_width=True)
    
    st.divider()
    
    # Фойдаланувчиларни тасдиқлаш қисми
    база = маълумотларни_юклаш()
    if not база.empty:
        янгилар = база[база['status'] == 0]
        st.subheader(f"🔔 Янги сўровлар: {len(янгилар)}")
        
        if not янгилар.empty:
            for i, row in янгилар.iterrows():
                with st.expander(f"👤 {row.get('name', 'Nomsiz')} | 📞 {row.get('phone', 'Nomersiz')}"):
                    st.write("Ушбу ходимни тизимга қўшишни тасдиқлайсизми?")
                    if st.button(f"✅ Тасдиқлаш ({row.get('phone')})", key=f"app_{i}"):
                        st.info("Жадвалга кириб, статус устунини 1 га ўзгартиринг.")
        
        st.divider()
        st.subheader("👥 Барча ходимлар")
        st.dataframe(база, use_container_width=True)
    else:
        st.error("Маълумотлар базасини юклаб бўлмади.")

st.markdown('<div style="text-align: center; color: white; margin-top: 50px; opacity: 0.7;">📞 Боғланиш: +998 88 754 98 96</div>', unsafe_allow_html=True)
