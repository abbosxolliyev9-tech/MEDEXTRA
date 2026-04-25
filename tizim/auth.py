import streamlit as st
import pandas as pd
import requests

# Google Sheets маълумотлари
БАЗА_URL = "https://docs.google.com/spreadsheets/d/1XyO5EqqDonEfQnmqr8j7SQNbVcx2SC93txhFVHoDGQA/export?format=csv"
# Охирги олинган Google Script URL линки
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwd02yRjdUap_qf72Gq-LXsnoRdE78XrDhViUr-eOCiWDF19nAg8rTKnqJtEBuhdf3A/exec"

def сессияни_тайёрлаш():
    if "auth" not in st.session_state:
        st.session_state["auth"] = False
    if "user" not in st.session_state:
        st.session_state["user"] = None
    if "role" not in st.session_state:
        st.session_state["role"] = 0

def маълумотларни_юклаш():
    try:
        df = pd.read_csv(БАЗА_URL)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

def кириш_ойнаси():
    st.markdown('<div class="blue-label"><h1>🔑 Тизимга кириш</h1></div>', unsafe_allow_html=True)
    б1, б2 = st.tabs(["🔒 Кириш", "📝 Рўйхатдан ўтиш"])
    
    with б1:
        тел = st.text_input("Логин (Телефон)", key="l_u")
        парол = st.text_input("Пароль", type="password", key="l_p")
        if st.button("КИРИШ", use_container_width=True):
            база = маълумотларни_юклаш()
            if not база.empty:
                қидирув = база[база['phone'].astype(str) == str(тел)]
                if not қидирув.empty and str(қидирув.iloc[0]['password']) == str(парол):
                    статус = int(қидирув.iloc[0]['status'])
                    if статус > 0:
                        st.session_state["auth"] = True
                        st.session_state["role"] = статус
                        st.session_state["user"] = қидирув.iloc[0].get('name', 'User')
                        st.rerun()
                    else:
                        st.warning("⚠️ Сўров тасдиқланмаган.")
                else:
                    st.error("❌ Логин ёки пароль хато!")

    with б2:
        исм = st.text_input("Исм шарифингиз", key="r_n")
        номер = st.text_input("Телефон рақамингиз", key="r_p")
        янги_парол = st.text_input("Пароль танланг", key="r_pass")
        if st.button("СЎРОВ ЮБОРИШ", use_container_width=True):
            if исм and номер and янги_парол:
                payload = {"phone": номер, "password": янги_парол, "name": исм}
                try:
                    # Google Script-га маълумот юбориш
                    res = requests.post(WEB_APP_URL, json=payload)
                    if res.status_code == 200:
                        st.success("✅ Сўров юборилди! Админ тасдиқлашини кутинг.")
                    else:
                        st.error("Юборишда хатолик юз берди.")
                except:
                    st.error("Сервер билан алоқа йўқ.")
