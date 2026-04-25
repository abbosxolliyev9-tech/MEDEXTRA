import streamlit as st

def apply_design():
    """Sayt dizayni"""
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
        label, h1, h2, h3, p, span { color: white !important; }
        .stButton>button {
            background-color: #27AE60 !important;
            color: white !important;
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)

def login_system():
    """Login tizimi"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        with st.container():
            st.markdown('<div class="main-block">', unsafe_allow_html=True)
            st.title("🔐 MEDEXTRA Tizimiga kirish")
            user = st.text_input("Login")
            pwd = st.text_input("Parol", type="password")
            if st.button("KIRISH"):
                if user == "admin" and pwd == "123":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Login yoki parol xato!")
            st.markdown('</div>', unsafe_allow_html=True)
        return False
    return True
