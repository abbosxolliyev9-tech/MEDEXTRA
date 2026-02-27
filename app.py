import streamlit as st
import pandas as pd
import io
import re
import math

# 1. Саҳифа созламалари
st.set_page_config(page_title="MEDEXTRA", page_icon="💊", layout="wide")

# 2. ОРҚА ФОН ВА ДИЗАЙН
def add_custom_style():
    # Сиз юклаган расмнинг линки
    bg_image_url = "https://raw.githubusercontent.com/abbosxolliyev9-tech/MEDEXTRA/main/unnamed.jpg"
    
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{bg_image_url}");
            background-attachment: fixed;
            background-size: cover;
            background-position: center;
        }}
        /* Кириш ойнасини марказга олиш ва чиройли қилиш */
        .login-container {{
            background-color: rgba(255, 255, 255, 0.9);
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0px 10px 25px rgba(0,0,0,0.3);
            max-width: 450px;
            margin: auto;
        }}
        .stButton>button {{
            background-color: #004a99;
            color: white;
            border-radius: 10px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

add_custom_style()

# 3. Логин тизими
def check_password():
    def password_entered():
        if st.session_state["password"] == "admin123" and st.session_state["user"] == "admin":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["user"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.write("<br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            st.markdown("<h2 style='text-align: center; color: #004a99;'>MEDEXTRA КИРИШ</h2>", unsafe_allow_html=True)
            st.text_input("Логин", key="user")
            st.text_input("Парол", type="password", key="password")
            st.button("Кириш", use_container_width=True, on_click=password_entered)
            if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                st.error("❌ Логин ёки парол хато!")
            st.markdown('</div>', unsafe_allow_html=True)
        return False
    return True

if check_password():
    # Тизим ичидаги қисм
    with st.sidebar:
        st.markdown("### 👨‍💼 Ишчи панель")
        if st.button("🚪 Чиқиш"):
            st.session_state.clear()
            st.rerun()

    st.markdown("<h1 style='color: white; text-shadow: 2px 2px 5px black; text-align: center;'>📋 Фармацевтика Ҳисоб-Китоб Тизими</h1>", unsafe_allow_html=True)
    st.markdown("---")

    # Сизнинг идеал ишлайдиган математик функсияларингиз
    def get_pack_size(name):
        match = re.search(r'[N№](\d+)', str(name).upper())
        return int(match.group(1)) if match else 1

    def calculate_prices(cost, pack_size):
        pachka_final = math.ceil((cost * 1.12) / 100) * 100
        dona_final = math.ceil((pachka_final / (pack_size if pack_size > 0 else 1)) / 100) * 100
        return pachka_final, dona_final

    # Файл юклаш қисми
    uploaded_file = st.file_uploader("📂 Excel (.xlsx) файлини танланг", type=['xlsx'])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        cols = df.columns.tolist()
        
        c1, c2 = st.columns(2)
        with c1:
            col_name = st.selectbox("Dori nomi ustuni:", cols, index=0)
        with c2:
            col_cost = st.selectbox("Tannarx (D) ustuni:", cols, index=3 if len(cols)>3 else 0)
        
        if st.button("🚀 ХИСОБЛАШНИ БОШЛАШ", use_container_width=True):
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
            st.success("✅ Ҳисоблаш якунланди!")
            st.dataframe(df)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            st.download_button("📥 НАТИЖАНИ ЮКЛАБ ОЛИШ", output.getvalue(), "medextra_hisobot.xlsx", use_container_width=True)
