import streamlit as st
import pandas as pd
import io
import re
import math

# 1. Саҳифа созламалари
st.set_page_config(page_title="MEDEXTRA", page_icon="💊", layout="wide")

# 2. ОРҚА ФОН ВА ДИЗАЙН (ФАҚАТ ШУ ҚИСМ ҚЎШИЛДИ)
def add_custom_style():
    bg_image_url = "https://raw.githubusercontent.com/abbosxolliyev9-tech/MEDEXTRA/main/pexels-eren-34577902.jpg"
    
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{bg_image_url}");
            background-attachment: fixed;
            background-size: cover;
            background-position: center;
        }}
        .login-card {{
            background-color: rgba(255, 255, 255, 0.95);
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0px 15px 35px rgba(0,0,0,0.4);
            max-width: 450px;
            margin: auto;
            text-align: center;
        }}
        .stTextInput label {{
            color: #1a1a1a !important;
            font-weight: bold !important;
        }}
        </style>
        """, 
        unsafe_allow_html=True
    )

add_custom_style()

# 3. ЛОГИН ФУНКЦИЯСИ
def check_password():
    def password_entered():
        if st.session_state["password"] == "admin123" and st.session_state["user"] == "admin":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["user"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.write("<br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            st.markdown('<div class="login-card">', unsafe_allow_html=True)
            st.markdown("<h1 style='color: #004a99;'>💊 MEDEXTRA</h1>", unsafe_allow_html=True)
            st.text_input("Логин", key="user")
            st.text_input("Парол", type="password", key="password")
            st.button("КИРИШ", use_container_width=True, on_click=password_entered)
            if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                st.error("❌ Логин ёки парол хато!")
            st.markdown('</div>', unsafe_allow_html=True)
        return False
    return True

# 4. АСОСИЙ ҲИСОБ-КИТОБ ҚИСМИ (ЎЗГАРМАГАН ҲОЛДА)
if check_password():
    with st.sidebar:
        st.markdown("### 👨‍💼 Ишчи панель")
        if st.button("🚪 Чиқиш"):
            st.session_state.clear()
            st.rerun()

    st.markdown("<h1 style='color: white; text-shadow: 2px 2px 10px black; text-align: center;'>📋 Ҳисоб-китоб панели</h1>", unsafe_allow_html=True)
    st.markdown("---")

    # Сизнинг ишлайдиган математик функцияларингиз
    def get_pack_size(name):
        match = re.search(r'[N№](\d+)', str(name).upper())
        return int(match.group(1)) if match else 1

    def calculate_prices(cost, pack_size):
        pachka_final = math.ceil((cost * 1.12) / 100) * 100
        dona_final = math.ceil((pachka_final / (pack_size if pack_size > 0 else 1)) / 100) * 100
        return pachka_final, dona_final

    # Excel билан ишлаш қисми
    uploaded_file = st.file_uploader("📂 Excel (.xlsx) файлини танланг", type=['xlsx'])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        cols = df.columns.tolist()
        
        c1, c2 = st.columns(2)
        with c1:
            col_name = st.selectbox("Dori nomi (Ustun):", cols, index=0)
        with c2:
            col_cost = st.selectbox("Tannarx (Ustun):", cols, index=3 if len(cols)>3 else 0)
        
        if st.button("🚀 ХИСОБЛАШ", use_container_width=True):
            p_list, d_list = [], []
            for _, row in df.iterrows():
                try:
                    val = str(row[col_cost]).replace(' ', '').replace(',', '.')
                    cost = float(re.sub(r'[^\d.]', '', val))
                except: cost = 0
                
                size = get_pack_size(row[col_name])
                p_p, d_p = calculate_prices(cost, size)
                p_list.append(p_p)
                d_list.append(d_p)
            
            df['Pachka Sotuv (H)'] = p_list
            df['Dona Narxi (I)'] = d_list
            st.success("✅ Тайёр!")
            st.dataframe(df)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            st.download_button("📥 НАТИЖАНИ ЮКЛАБ ОЛИШ", output.getvalue(), "medextra_final.xlsx", use_container_width=True)
