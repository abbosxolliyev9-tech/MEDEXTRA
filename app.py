import streamlit as st
import pandas as pd
import io
import re
import math

# 1. Саҳифа созламалари
st.set_page_config(page_title="MEDEXTRA", page_icon="💊", layout="wide")

# 2. ДИЗАЙН (CSS) - МАТНЛАРНИ ОҚ БЛОК ИЧИГА ОЛИШ
def add_custom_style():
    bg_image_url = "https://raw.githubusercontent.com/abbosxolliyev9-tech/MEDEXTRA/main/unnamed.jpg"
    
    st.markdown(
        f"""
        <style>
        /* Умумий орқа фон */
        .stApp {{
            background-image: url("{bg_image_url}");
            background-attachment: fixed;
            background-size: cover;
            background-position: center;
        }}
        
        /* ЛОГИН УЧУН МАХСУС ОҚ ТЎРТБУРЧАК (CARD) */
        .login-card {{
            background-color: rgba(255, 255, 255, 0.95);
            padding: 50px;
            border-radius: 25px;
            box-shadow: 0px 20px 40px rgba(0,0,0,0.4);
            text-align: center;
            border: 1px solid #e0e0e0;
        }}
        
        /* "Логин" ва "Парол" ёзувларини қора қилиш */
        .stTextInput label {{
            color: #1a1a1a !important;
            font-weight: bold !important;
            font-size: 16px !important;
        }}
        
        /* Кириш тугмасининг ранги */
        .stButton>button {{
            background-color: #004a99 !important;
            color: white !important;
            border-radius: 12px !important;
            height: 3.5em !important;
            font-weight: bold !important;
            margin-top: 20px;
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
        # Экранни марказлаштириш учун устунлар
        st.write("<br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1.3, 1])
        
        with col2:
            # --- ОҚ ТЎРТБУРЧАКНИ БОШЛАШ ---
            st.markdown('<div class="login-card">', unsafe_allow_html=True)
            
            # Логотип ва Сарлавҳа (Блок ичида)
            st.markdown("<h1 style='color: #004a99; font-size: 45px; margin-bottom: 0;'>💊 MEDEXTRA</h1>", unsafe_allow_html=True)
            st.markdown("<p style='color: #555; font-size: 16px; margin-bottom: 30px;'>Фармацевтика тизимига кириш</p>", unsafe_allow_html=True)
            
            # Киритиш майдонлари
            st.text_input("Логин", key="user", placeholder="admin")
            st.text_input("Парол", type="password", key="password", placeholder="******")
            
            # Тугма
            st.button("ТИЗИМГА КИРИШ", use_container_width=True, on_click=password_entered)
            
            if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                st.error("❌ Логин ёки парол хато!")
            
            st.markdown('</div>', unsafe_allow_html=True)
            # --- ОҚ ТЎРТБУРЧАКНИ ЁПИШ ---
            
        return False
    return True

# 4. Асосий Ишчи Қисм
if check_password():
    with st.sidebar:
        st.markdown("### 👨‍💼 Админ: admin")
        if st.button("🚪 Чиқиш"):
            st.session_state.clear()
            st.rerun()

    st.markdown("<h1 style='color: white; text-shadow: 3px 3px 10px black; text-align: center; font-size: 45px;'>📋 Ҳисоб-китоб панели</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Сизнинг ишлаб турган Excel ҳисоблаш кодларингиз шу ерда қолади...
    uploaded_file = st.file_uploader("📂 Excel файлини юкланг", type=['xlsx'])
    if uploaded_file:
        st.success("Файл юкланди, энди ҳисоблашингиз мумкин!")
