import streamlit as st

def apply_design():
    st.markdown("""
        <style>
        .stApp {
            background-image: url("https://images.unsplash.com/photo-1587854692152-cbe660feec90?q=80&w=2070");
            background-size: cover;
            background-attachment: fixed;
        }
        .main-block {
            background: rgba(0, 0, 0, 0.85);
            padding: 25px;
            border-radius: 15px;
            color: white;
            border: 1px solid #27AE60;
        }
        .stButton>button {
            background-color: #27AE60 !important;
            color: white !important;
            border-radius: 10px !important;
            font-weight: bold !important;
        }
        label, h1, h2, h3, p, span { color: white !important; }
        </style>
    """, unsafe_allow_html=True)

def login_system():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        with st.form("login_form"):
            st.title("🔐 Kirish")
            user = st.text_input("Login")
            pwd = st.text_input("Parol", type="password")
            if st.form_submit_button("Kirish"):
                if user == "admin" and pwd == "123": # O'zingizga moslang
                    st.session_state.logged_in = True
                    st.session_state.user_role = "admin"
                    st.rerun()
                else:
                    st.error("Xato!")
        return False
    return True
