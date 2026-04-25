import streamlit as st

def сессияни_тайёрлаш():
    """Сайт очилганда хотирани созлаш"""
    if "auth" not in st.session_state:
        st.session_state["auth"] = False
    if "user" not in st.session_state:
        st.session_state["user"] = None

def чиқиш_тугмаси():
    """ Sidebar-да чиқиш тугмасини кўрсатиш """
    if st.session_state.get("auth"):
        st.sidebar.markdown("---")
        st.sidebar.write(f"👤: **{st.session_state['user']}**")
        if st.sidebar.button("🚪 Тизимдан чиқиш"):
            st.session_state["auth"] = False
            st.session_state["user"] = None
            st.rerun()

def кириш_ойнаси():
    """ Кириш ва Рўйхатдан ўтиш ойнаси """
    st.title("🏥 MEDEXTRA Тизими")
    
    бўлим1, бўлим2 = st.tabs(["🔑 Кириш", "📝 Рўйхатдан ўтиш"])
    
    with бўлим1:
        логин = st.text_input("Логин", key="login_val")
        парол = st.text_input("Пароль", type="password", key="pass_val")
        
        if st.button("Кириш"):
            # Бу ерда оддий текширув: логин: admin, парол: 123
            if логин == "admin" and парол == "123":
                st.session_state["auth"] = True
                st.session_state["user"] = "Администратор"
                st.success("Хуш келибсиз!")
                st.rerun()
            else:
                st.error("Логин ёки пароль хато!")

    with бўлим2:
        st.subheader("Янги ходимни қўшиш")
        st.info("Рўйхатдан ўтиш бўлими ҳозирча ёпиқ. Администраторга мурожаат қилинг.")
