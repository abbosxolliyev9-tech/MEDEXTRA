import streamlit as st
import pandas as pd
import io
import zipfile
import re
# Сиздаги папка ва файл номига мосланди:
from calculations.logic import calculate_logic, get_pack_size

# --- ДИЗАЙН ВА ФОН ---
st.set_page_config(page_title="MEDEXTRA", layout="wide")

st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("pexels-eren-34577902.jpg");
        background-size: cover;
        background-attachment: fixed;
    }}
    .main-block {{
        background-color: rgba(0, 0, 255, 0.4); 
        padding: 30px;
        border-radius: 15px;
        border: 2px solid #27AE60;
        color: white !important;
    }}
    .stMarkdown, label, p, h1, h2, h3 {{
        color: white !important;
        background-color: rgba(39, 174, 96, 0.6); 
        padding: 5px;
        border-radius: 5px;
    }}
    .stButton>button {{
        background-color: #27AE60 !important;
        color: white !important;
        font-weight: bold;
    }}
    </style>
""", unsafe_allow_html=True)

# --- ЛОГИН ТИЗИМИ ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<div class="main-block">', unsafe_allow_html=True)
    st.title("🔐 MEDEXTRA КИРИШ")
    u = st.text_input("Логин (admin)")
    p = st.text_input("Пароль (Abbos96)", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 КИРИШ"):
            if u == "admin" and p == "Abbos96":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Хато!")
    with col2:
        if st.button("📝 РЕГИСТРАЦИЯ"):
            st.info("Админ тасдиқлашини кутинг.")
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- АСОСИЙ ИШЧИ ҚИСМ ---
    choice = st.sidebar.radio("Бўлимлар:", ["Админ Ҳисоб", "Мижоз Ҳисоб", "Админ Панель"])
    
    if st.sidebar.button("🚪 Чиқиш"):
        st.session_state.logged_in = False
        st.rerun()

    st.markdown('<div class="main-block">', unsafe_allow_html=True)
    st.title(f"📊 {choice}")

    if choice in ["Админ Ҳисоб", "Мижоз Ҳисоб"]:
        files = st.file_uploader("Экзелларни танланг", type=['xlsx'], accept_multiple_files=True)
        
        m_val = 10
        if choice == "Мижоз Ҳисоб":
            m_val = st.slider("Устама фоизи (%)", 1, 20, 10)

        if files and st.button("🚀 ҲИСОБЛАШ"):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_f:
                for file in files:
                    df = pd.read_excel(file)
                    
                    # Устунларни автоматик қидириш
                    p_res = []
                    for _, row in df.iterrows():
                        try:
                            # 4-устун (индекс 3) - Нарх
                            cost = float(str(row.iloc[3]).replace(' ', '').replace(',', '.'))
                            # 1-устун (индекс 0) - Номи
                            size = get_pack_size(row.iloc[0])
                            res = calculate_logic(cost, choice, m_val)
                            p_res.append(res)
                        except:
                            p_res.append(0)
                    
                    df['Янги Нарх'] = p_res
                    buf = io.BytesIO()
                    df.to_excel(buf, index=False)
                    zip_f.writestr(file.name, buf.getvalue())
            
            st.success("✅ Тайёр!")
            st.download_button("📥 ZIP ЮКЛАШ", zip_buffer.getvalue(), "natijalar.zip")

    elif choice == "Админ Панель":
        st.write("🌐 Google Sheets: [Очиш](https://docs.google.com/spreadsheets/d/1XyO5EqqDonEfQnmqr8j7SQNbVcx2SC93txhFVHoDGQA/edit)")

    st.markdown('</div>', unsafe_allow_html=True)
