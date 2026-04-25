import streamlit as st
import pandas as pd
import hashlib

# 1. МАЪЛУМОТЛАР БАЗАСИ
БАЗА_URL = "https://docs.google.com/spreadsheets/d/1XyO5EqqDonEfQnmqr8j7SQNbVcx2SC93txhFVHoDGQA/export?format=csv"

def маълумотларни_юклаш():
    try:
        df = pd.read_csv(БАЗА_URL)
        # Устун номларидаги бўш жойларни олиб ташлаймиз
        df.columns = [c.strip().lower() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Базага уланишда хатолик: {e}")
        return pd.DataFrame()

def сессияни_тайёрлаш():
    if "auth" not in st.session_state:
        st.session_state["auth"] = False
    if "user" not in st.session_state:
        st.session_state["user"] = None
    if "role" not in st.session_state:
        st.session_state["role"] = 0

def чиқиш_тугмаси():
    if st.session_state.get("auth"):
        st.sidebar.markdown("---")
        st.sidebar.write(f"👤: **{st.session_state['user']}**")
        if st.sidebar.button("🚪 Чиқиш"):
            st.session_state["auth"] = False
            st.rerun()

def кириш_ойнаси():
    st.markdown('<div style="text-align: center;"><h1>🏥 MEDEXTRA</h1></div>', unsafe_allow_html=True)
    бўлим1, бўлим2 = st.tabs(["🔑 Кириш", "📝 Рўйхатдан ўтиш"])

    with бўлим1:
        тел = st.text_input("Логин (Телефон)", key="l_phone")
        парол = st.text_input("Пароль", type="password", key="l_pass")
        
        if st.button("КИРИШ", use_container_width=True):
            база = маълумотларни_юклаш()
            
            if база.empty:
                st.error("База бўш ёки юкланмади!")
                return

            # Пароль хэши
            парол_хэш = hashlib.sha256(парол.encode()).hexdigest()
            
            # Устун номини аниқлаймиз (phone ёки телефон бўлиши мумкин)
            phone_col = 'phone' if 'phone' in база.columns else база.columns[0]
            
            # Қидирув
            қидирув = база[база[phone_col].astype(str).str.lower() == str(тел).lower()]
            
            if not қидирув.empty:
                # Пароль ва статус устунларини топамиз
                pass_col = 'password' if 'password' in база.columns else база.columns[1]
                stat_col = 'status' if 'status' in база.columns else база.columns[-1]
                name_col = 'name' if 'name' in база.columns else база.columns[2]
                
                дб_парол = str(қидирув.iloc[0][pass_col])
                статус = int(қидирув.iloc[0][stat_col])
                
                if (дб_парол == парол_хэш or дб_парол == парол):
                    if статус > 0:
                        st.session_state["auth"] = True
                        st.session_state["user"] = қидирув.iloc[0][name_col]
                        st.session_state["role"] = статус
                        st.success("Хуш келибсиз!")
                        st.rerun()
                    else:
                        st.warning("⚠️ Статусингиз актив эмас!")
                else:
                    st.error("❌ Пароль хато!")
            else:
                st.error("❌ Фойдаланувчи топилмади!")

    with бўлим2:
        st.info("📝 Рўйхатдан ўтиш учун Администраторга мурожаат қилинг.")
