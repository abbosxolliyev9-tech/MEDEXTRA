import streamlit as st
import pandas as pd
import hashlib

# 1. МАЪЛУМОТЛАР БАЗАСИ (GOOGLE SHEETS)
БАЗА_URL = "https://docs.google.com/spreadsheets/d/1XyO5EqqDonEfQnmqr8j7SQNbVcx2SC93txhFVHoDGQA/export?format=csv"

def маълумотларни_юклаш():
    try:
        # Кешдан фойдаланмай янги маълумотларни олиш
        return pd.read_csv(БАЗА_URL)
    except Exception as e:
        st.error(f"Базага уланишда хатолик: {e}")
        return pd.DataFrame(columns=['phone', 'password', 'name', 'status'])

def сессияни_тайёрлаш():
    """Сайт юкланганда хотирани созлаш"""
    if "auth" not in st.session_state:
        st.session_state["auth"] = False
    if "user" not in st.session_state:
        st.session_state["user"] = None
    if "role" not in st.session_state:
        st.session_state["role"] = 0

def чиқиш_тугмаси():
    """Sidebar-да чиқиш тугмасини чиқариш"""
    if st.session_state.get("auth"):
        st.sidebar.markdown("---")
        st.sidebar.write(f"👤 Фойдаланувчи: **{st.session_state['user']}**")
        if st.sidebar.button("🚪 Тизимдан чиқиш"):
            st.session_state["auth"] = False
            st.session_state["user"] = None
            st.session_state["role"] = 0
            st.rerun()

def кириш_ойнаси():
    """Асосий кириш ва рўйхатдан ўтиш интерфейси"""
    st.markdown('<div style="text-align: center;"><h1>🏥 MEDEXTRA Тизими</h1></div>', unsafe_allow_html=True)
    
    бўлим1, бўлим2 = st.tabs(["🔑 Кириш", "📝 Рўйхатдан ўтиш"])

    with бўлим1:
        st.markdown("### Тизимга кириш")
        тел = st.text_input("Логин ёки Телефон", placeholder="Масалан: admin ёки 998901234567", key="input_login")
        парол = st.text_input("Пароль", type="password", key="input_pass")
        
        if st.button("КИРИШ", use_container_width=True):
            база = маълумотларни_юклаш()
            
            # Киритилган паролни шифрлаш
            парол_хэш = hashlib.sha256(парол.encode()).hexdigest()
            
            # Логин бўйича қидириш (Телефон ёки 'admin' сўзи бўйича)
            қидирув = база[(база['phone'].astype(str).lower() == str(тел).lower())]
            
            if not қидирув.empty:
                дб_парол = str(қидирув.iloc[0]['password'])
                статус = int(қидирув.iloc[0]['status'])
                исм = қидирув.iloc[0]['name']
                
                # ПАРОЛЬ ВА СТАТУСНИ ТЕКШИРИШ
                if (дб_парол == парол_хэш or дб_парол == парол):
                    if статус > 0:
                        st.session_state["auth"] = True
                        st.session_state["user"] = исм
                        st.session_state["role"] = статус
                        st.success(f"Хуш келибсиз, {исм}!")
                        st.rerun()
                    else:
                        # Статус 0 бўлган ҳолат
                        st.warning("⚠️ Сизнинг сўровингиз ҳали тасдиқланмаган. Илтимос, админ тасдиқлашини кутинг.")
                else:
                    st.error("❌ Пароль хато!")
            else:
                st.error("❌ Бундай логинли фойдаланувчи топилмади!")

    with бўлим2:
        st.subheader("📝 Янги ҳисоб учун сўров")
        янги_исм = st.text_input("Исм шарифингиз")
        янги_тел = st.text_input("Телефон рақамингиз (Кейинчалик логин бўлади)")
        янги_парол = st.text_input("Пароль танланг", type="password")
        
        if st.button("СЎРОВ ЮБОРИШ", use_container_width=True):
            if янги_исм and янги_тел and янги_парол:
                st.info(f"✅ Ҳурматли {янги_исм}, сўровингиз юборилди!")
                st.success("Админ сизни жадвалда тасдиқлаши (статусни 1 қилиши) билан тизимга кира оласиз.")
                st.markdown("""
                **Кейинги қадамлар:**
                1. Рақамингизни админга айтинг.
                2. Админ сизни базага қўшиб, статус беради.
                3. Кейин 'Кириш' бўлими орқали киринг.
                """)
            else:
                st.error("Илтимос, ҳамма катакларни тўлдиринг!")
