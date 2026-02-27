import streamlit as st
import pandas as pd
import io
import re
import math

# 1. Саҳифа созламалари
st.set_page_config(page_title="MEDEXTRA", page_icon="💊", layout="wide")

# 2. ОРҚА ФОН ВА ОҚ ТЎРТБУРЧАК ДИЗАЙНИ
def add_custom_style():
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
        /* МАТНЛАР УЧУН ОҚ ТЎРТБУРЧАК (КОНТЕЙНЕР) */
        .login-card {{
            background-color: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0px 15px 35px rgba(0,0,0,0.4);
            max-width: 420px;
            margin: auto;
            border: 1px solid #e0e0e0;
            text-align: center;
        }}
        /* Логин ва Парол сўзлари ранги */
        .stTextInput label {{
            color: #333333 !important;
            font-weight: 600 !important;
            display: flex;
            justify-content: flex-start;
        }}
        /* Кириш тугмаси */
        .stButton>button {{
            background-color: #0056b3;
            color: white;
            border-radius: 8px;
            font-weight: bold;
            height: 3.5em;
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
        st.write("<br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1.2, 1]) # Ортадаги устун кенглиги
        
        with col2:
            # ОҚ ТЎРТБУРЧАКНИ БОШЛАШ
            st.markdown('<div class="login-card">', unsafe_allow_html=True)
            
            st.markdown("<h1 style='color: #0056b3; margin-bottom: 5px;'>💊 MEDEXTRA</h1>", unsafe_allow_html=True)
            st.markdown("<p style='color: #666; font-size: 14px;'>Фармацевтика тизимига кириш</p>", unsafe_allow_html=True)
            st.markdown("<hr style='margin-bottom: 25px;'>", unsafe_allow_html=True)
            
            # Кириш майдонлари
            st.text_input("Логин", key="user")
            st.text_input("Парол", type="password", key="password")
            
            st.button("ТИЗИМГА КИРИШ", use_container_width=True, on_click=password_entered)
            
            if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                st.error("Хато: Логин ёки парол нотўғри")
            
            # ОҚ ТЎРТБУРЧАКНИ ЁПИШ
            st.markdown('</div>', unsafe_allow_html=True)
            
        return False
    return True

if check_password():
    # Асосий саҳифа (Тизим ичи)
    with st.sidebar:
        st.markdown("### ⚙️ Созламалар")
        if st.button("🚪 Чиқиш"):
            st.session_state.clear()
            st.rerun()

    st.markdown("<h1 style='color: white; text-shadow: 2px 2px 10px rgba(0,0,0,0.8); text-align: center;'>💊 MEDEXTRA ИШЧИ ПАНЕЛИ</h1>", unsafe_allow_html=True)
    
    # ... Бу ерда ҳисоблаш кодингиз давом этади ...
