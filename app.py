import streamlit as st
import pandas as pd
from calculations.logic import process_excel_files
# Эслатма: Агар папка номини GitHub'да 'tizim' деб ўзгартирган бўлсангиз, 'тизим'ни 'tizim'га алмаштиринг
from тизим.кириш import сессияни_тайёрлаш, кириш_ойнаси, маълумотларни_юклаш

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

if rol == 9:
    menu = st.sidebar.radio("Бўлимни танланг:", ["🚀 Админ Ҳисоб", "📊 Фоизли Кальк", "⚙️ Панел"])
else:
    menu = st.sidebar.radio("Бўлимни танланг:", ["📊 Фоизли Кальк"])

st.sidebar.markdown("---")
st.sidebar.write(f"👤 Фойдаланувчи: **{st.session_state['user']}**")
if st.sidebar.button("🚪 Тизимдан чиқиш"):
    st.session_state["auth"] = False
    st.rerun()

# 5. Ишчи бўлимлар
if menu == "🚀 Админ Ҳисоб" or menu == "📊 Фоизли Кальк":
    st.markdown(f'<div class="blue-label">{menu.upper()}</div>', unsafe_allow_html=True)
    
    pct = None
    if menu == "📊 Фоизли Кальк":
        pct = st.slider("Устама фоизини танланг (%):", 1, 25, 12)
    
    files = st.file_uploader("Excel файлларни юкланг", type=['xlsx'], accept_multiple_files=True)
    
    if files:
        # Биринчи файлни ўқиб устунларни олиш
        df_temp = pd.read_excel(files[0])
        cols = df_temp.columns.tolist()
        
        c1, c2 = st.columns(2)
        col_n = c1.selectbox("💊 Дори номи устуни:", cols)
        col_c = c2.selectbox("💰 Таннарх устуни:", cols, index=min(4, len(cols)-1))
        
        if st.button("🚀 ҲИСОБЛАШНИ БОШЛАШ", use_container_width=True):
            with st.spinner("Файллар қайта ишланмоқда..."):
                zip_data = process_excel_files(files, menu, col_n, col_c, pct)
                st.success("✅ Ҳисоблаш муваффақиятли якунланди!")
                st.download_button(
                    label="📥 ТАЙЁР ФАЙЛЛАРНИ ЮКЛАБ ОЛИШ (ZIP)",
                    data=zip_data,
                    file_name="MedExtra_Natija.zip",
                    mime="application/zip",
                    use_container_width=True
                )

elif menu == "⚙️ Панел":
    st.markdown('<div class="blue-label">⚙️ БОШҚАРУВ ПАНЕЛИ</div>', unsafe_allow_html=True)
    
    # Google Sheets тугмаси
    sheet_url = "https://docs.google.com/spreadsheets/d/1XyO5EqqDonEfQnmqr8j7SQNbVcx2SC93txhFVHoDGQA/edit"
    st.link_button("📂 Google Sheets Базасини Очиш", sheet_url, use_container_width=True)
    
    st.divider()
    
    # Фойдаланувчиларни бошқариш
    база = маълумотларни_юклаш()
    if not база.empty:
        # Статуси 0 бўлганларни қидириш (Янги сўровлар)
        s_col = 'status' if 'status' in база.columns else база.columns[-1]
        янгилар = база[база[s_col].astype(int) == 0]
        
        st.subheader(f"🔔 Янги сўровлар: {len(янгилар)}")
        
        if not янгилар.empty:
            for i, row in янгилар.iterrows():
                with st.expander(f"👤 {row.get('name', 'Nomsiz')} ({row.get('phone', '📞')})"):
                    st.write("Тизимга кириш учун рухсат берасизми?")
                    if st.button(f"✅ Тасдиқлаш", key=f"btn_ok_{i}"):
                        st.info("Илтимос, Google Sheets жадвалига кириб, ушбу ходимнинг статусини 1 қилиб ўзгартиринг.")
        
        st.divider()
        st.subheader("👥 Барча ходимлар рўйхати")
        st.dataframe(база, use_container_width=True)
    else:
        st.error("Маълумотлар базасини юклашда хатолик юз берди.")

# 6. Footer (Пастки қисм)
st.markdown('<div style="text-align: center; color: white; margin-top: 50px; opacity: 0.7;">📞 Техник ёрдам: +998 88 754 98 96</div>', unsafe_allow_html=True)
