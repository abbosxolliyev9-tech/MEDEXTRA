import streamlit as st
import pandas as pd
import hashlib

БАЗА_URL = "https://docs.google.com/spreadsheets/d/1XyO5EqqDonEfQnmqr8j7SQNbVcx2SC93txhFVHoDGQA/export?format=csv"

def маълумотларни_юклаш():
    try:
        df = pd.read_csv(БАЗА_URL)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

def сессияни_тайёрлаш():
    if "auth" not in st.session_state: st.session_state["auth"] = False
    if "user" not in st.session_state: st.session_state["user"] = None
    if "role" not in st.session_state: st.session_state["role"] = 0

def кириш_ойнаси():
    st.markdown('<div style="text-align: center; color: white;"><h1>🏥 MEDEXTRA</h1></div>', unsafe_allow_html=True)
    б1, б2 = st.tabs(["🔑 Кириш", "📝 Рўйхатдан ўтиш"])
    
    with б1:
        тел = st.text_input("Логин (Телефон)", key="l_u")
        парол = st.text_input("Пароль", type="password", key="l_p")
        if st.button("КИРИШ", use_container_width=True):
            база = маълумотларни_юклаш()
            p_col = 'phone' if 'phone' in база.columns else база.columns[0]
            қидирув = база[база[p_col].astype(str) == str(тел)]
            if not қидирув.empty:
                # Пароль ва статус текшируви шу ерда бўлади
                st.session_state["auth"] = True
                st.session_state["role"] = int(қидирув.iloc[0]['status'])
                st.session_state["user"] = қидирув.iloc[0]['name']
                st.rerun()

    with б2:
        st.subheader("📝 Янги ходим қўшиш")
        st.text_input("Исм шарифингиз", key="r_n")
        st.text_input("Телефон", key="r_p")
        if st.button("СЎРОВ ЮБОРИШ"):
            st.success("✅ Сўров юборилди! Админ сизни тасдиқлашини кутинг.")
