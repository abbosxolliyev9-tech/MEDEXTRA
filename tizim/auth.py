import streamlit as st

BACKGROUND_IMAGE = "pexels-eren-34577902.jpg" 
CONTACT_PHONE = "+998887549896"

def apply_design():
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("https://raw.githubusercontent.com/Abbos-96/medextra/main/{BACKGROUND_IMAGE}");
            background-size: cover;
            background-attachment: fixed;
        }}
        .main-block {{
            background: rgba(0, 0, 0, 0.85);
            padding: 25px;
            border-radius: 15px;
            color: white;
            border: 1px solid #27AE60;
        }}
        .footer {{
            position: fixed;
            left: 0; bottom: 0; width: 100%;
            background-color: rgba(0, 0, 0, 0.8);
            color: white; text-align: center;
            padding: 10px; font-size: 16px; z-index: 1000;
        }}
        </style>
        <div class="footer">Bog'lanish uchun: {CONTACT_PHONE}</div>
    """, unsafe_allow_html=True)

def login_system():
    apply_design()
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_role = None

    if not st.session_state.logged_in:
        st.markdown('<div class="main-block">', unsafe_allow_html=True)
        st.title("💊 MEDEXTRA: Kirish")
        
        user = st.text_input("Login")
        pw = st.text_input("Parol", type="password")
        
        col1, col2 = st.columns(2)
        if col1.button("Kirish"):
            if user == "admin" and pw == "Abbos96":
                st.session_state.logged_in = True
                st.session_state.user_role = "admin"
                st.rerun()
            elif user == "mijoz": # Вақтинчалик мижоз логини
                st.session_state.logged_in = True
                st.session_state.user_role = "mijoz"
                st.rerun()
            else:
                st.error("Login yoki parol noto'g'ri!")
        
        st.info("Mijoz bo'lib kirish uchun login: 'mijoz', parol: '123' (vaqtincha)")
        st.markdown('</div>', unsafe_allow_html=True)
