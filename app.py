import streamlit as st
import pandas as pd
import io
import zipfile
import re
import os
# Papka nomiga e'tibor bering: calculations
from calculations.logic import calculate_logic, get_pack_size

# --- 1. DIZAYN VA FONDAGI RASM ---
st.set_page_config(page_title="MEDEXTRA", layout="wide")

# Fondagi rasm borligini tekshirish
bg_image = "pexels-eren-34577902.jpg"
bg_style = ""
if os.path.exists(bg_image):
    bg_style = f"""
        background-image: url("https://raw.githubusercontent.com/{st.secrets.get('GITHUB_USERNAME', 'abbosxolliyev9-tech')}/MEDEXTRA/main/{bg_image}");
        background-size: cover;
        background-attachment: fixed;
    """
else:
    bg_style = "background-color: #0E1117;" # Rasm bo'lmasa qora fon

st.markdown(f"""
    <style>
    .stApp {{
        {bg_style}
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
        width: 100%;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 2. LOGIN TIZIMI ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<div class="main-block">', unsafe_allow_html=True)
    st.title("🔐 MEDEXTRA KIRISH")
    
    u = st.text_input("Логин")
    p = st.text_input("Пароль", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 КИРИШ"):
            if u == "admin" and p == "Abbos96":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Login yoki parol xato!")
    with col2:
        if st.button("📝 РЕГИСТРАЦИЯ"):
            st.info("Admin tasdiqlashini kuting.")
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- 3. ASOSIY QISM ---
    choice = st.sidebar.radio("Bo'limlar:", ["Админ Ҳисоб", "Мижоз Ҳисоб", "Админ Панель"])
    
    if st.sidebar.button("🚪 Chiqish"):
        st.session_state.logged_in = False
        st.rerun()

    st.markdown('<div class="main-block">', unsafe_allow_html=True)
    st.title(f"📊 {choice}")

    if choice in ["Админ Ҳисоб", "Мижоз Ҳisob"]:
        files = st.file_uploader("Excel fayllarni tanlang", type=['xlsx'], accept_multiple_files=True)
        
        m_val = 10
        if choice == "Мижоз Ҳисоб":
            m_val = st.sidebar.slider("Ustama %", 1, 20, 10)

        if files and st.button("🚀 HISOBLASH"):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_f:
                for file in files:
                    df = pd.read_excel(file)
                    p_res = []
                    for _, row in df.iterrows():
                        try:
                            # 4-ustun (index 3) - Narx
                            cost = float(str(row.iloc[3]).replace(' ', '').replace(',', '.'))
                            # 1-ustun (index 0) - Nomi
                            size = get_pack_size(row.iloc[0])
                            res = calculate_logic(cost, choice, m_val)
                            p_res.append(res)
                        except:
                            p_res.append(0)
                    
                    df['Yangi Narx'] = p_res
                    excel_buf = io.BytesIO()
                    df.to_excel(excel_buf, index=False)
                    zip_f.writestr(file.name, excel_buf.getvalue())
            
            st.success("Tayyor!")
            st.download_button("📥 ZIP YUKLASH", zip_buffer.getvalue(), "medextra_results.zip")

    elif choice == "Админ Панель":
        st.write("🌐 Google Sheets: [Ochish](https://docs.google.com/spreadsheets/d/1XyO5EqqDonEfQnmqr8j7SQNbVcx2SC93txhFVHoDGQA/edit)")

    st.markdown('</div>', unsafe_allow_html=True)
