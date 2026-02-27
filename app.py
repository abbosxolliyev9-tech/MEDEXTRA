import streamlit as st
import pandas as pd
import io
import re
import math

# 1. Саҳифа созламалари
st.set_page_config(page_title="MEDEXTRA", page_icon="💊", layout="wide")

# 2. ЯНГИ РАСМ ВА ОҚ БЛОК ДИЗАЙНИ (CSS)
def add_custom_style():
    # Сиз юклаган янги расмнинг GitHub линки
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
        
        /* ЛОГИН УЧУН ОҚ ТЎРТБУРЧАК (CARD) */
        .login-card {{
            background-color: rgba(255, 255, 255, 0.96); /* Деярли шаффоф бўлмаган оқ ранг */
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0px 15px 35px rgba(0,0,0,0.4);
            max-width: 450px;
            margin: auto;
            border: 1px solid #e0e0e0;
            text-align: center;
        }}
        
        /* Матн ва белгиларни қора қилиш */
        .stTextInput label {{
            color: #1a1a1a !important;
            font-weight: bold !important;
            display: flex;
        }}
        
        .stButton>button {{
            background-color: #004a99 !important;
            color: white !important;
            border-radius: 10px !important;
            height: 3.5em !important;
            font-weight: bold !important;
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
        col1, col2, col3 = st.columns([1, 1.2, 1])
        
        with col2:
            st.markdown('<div class="login-card">', unsafe_allow_html=True)
            st.markdown("<h1 style='color: #004a99; margin-bottom: 5px;'>💊 MEDEXTRA</h1>", unsafe_allow_html=True)
            st.markdown("<p style='color: #555;'>Тизимга кириш учун маълумотларни киритинг</p>", unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            
            st.text_input("Логин", key="user")
            st.text_input("Парол", type="password", key="password")
            
            st.button("КИРИШ", use_container_width=True, on_click=password_entered)
            
            if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                st.error("❌ Логин ёки парол хато!")
            st.markdown('</div>', unsafe_allow_html=True)
        return False
    return True

if check_password():
    # Асосий қисм (Тизим ичи)
    st.sidebar.markdown("### 👨‍💼 Админ")
    if st.sidebar.button("🚪 Чиқиш"):
        st.session_state.clear()
        st.rerun()

    st.markdown("<h1 style='color: white; text-shadow: 2px 2px 10px black; text-align: center;'>📋 Ҳисоб-китоб панели</h1>", unsafe_allow_html=True)
    
    # Бу ерда Excel билан ишлайдиган кодингиз давом этади...
