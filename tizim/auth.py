import streamlit as st

def apply_design():
    st.markdown("""
        <style>
        .stApp { background-color: #0E1117; color: white; }
        .main-block { background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 15px; border: 1px solid #27AE60; }
        label, h1, h2, h3, p, span { color: white !important; }
        .stButton>button { background-color: #27AE60 !important; color: white !important; width: 100%; }
        </style>
    """, unsafe_allow_html=True)

def login_system():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if not st.session_state.logged_in:
        with st.container():
            st.markdown('<div class="main-block">', unsafe_allow_html=True)
            st.title("🔐 MEDEXTRA Kirish")
            u = st.text_input("Login")
            p = st.text_input("Parol", type="password")
            if st.button("KIRISH"):
                if u == "admin" and p == "123":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Xato!")
            st.markdown('</div>', unsafe_allow_html=True)
        return False
    return True
