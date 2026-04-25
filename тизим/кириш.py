import streamlit as st
import pandas as pd
import hashlib

БАЗА_URL = "https://docs.google.com/spreadsheets/d/1XyO5EqqDonEfQnmqr8j7SQNbVcx2SC93txhFVHoDGQA/export?format=csv"

def маълумотларни_юклаш():
    try:
        df = pd.read_csv(БАЗА_URL)
        df.columns = [c.strip().lower() for c in df.columns]
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
        тел = st.text_input("Логин (Телефон ёки 'admin')")
        парол = st.text_input("Пароль", type="password")
        if st.button("КИРИШ", use_container_width=True):
            база = маълумотларни_юклаш()
            if база.empty: 
                st.error("Базага уланиб бўлмади")
                return
            
            p_col = 'phone' if 'phone' in база.columns else база.columns[0]
            қидирув = база[база[p_col].astype(str).str.lower() == str(тел).lower()]
            
            if not қидирув.empty:
                дб_парол = str(қидирув.iloc[0]['password'])
                статус = int(қидирув.iloc[0]['status'])
                парол_хэш = hashlib.sha256(парол.encode()).hexdigest()
                
                if (дб_парол == парол_хэш or дб_парол == парол):
                    if статус > 0:
                        st.session_state["auth"] = True
                        st.session_state["user"] = қидирув.iloc[0]['name']
                        st.session_state["role"] = статус
                        st.rerun()
                    else:
                        st.warning("⚠️ Сизнинг сўровингиз тасдиқланмаган.")
                else: st.error("❌ Пароль хато")
            else: st.error("❌ Фойдаланувчи топилмади")

    with б2:
        st.subheader("Янги фойдаланувчи")
        st.write("Рўйхатдан ўтиш учун маълумотларни киритинг:")
        st.text_input("Исм шарифингиз")
        st.text_input("Телефон рақам")
        st.text_input("Пароль танланг", type="password")
        if st.button("РЎЙХАТДАН ЎТИШ"):
            st.success("✅ Сўров юборилди! Админ тасдиқлагандан кейин киришингиз мумкин.")
            st.info("Боғланиш: +998 88 754 98 96")
