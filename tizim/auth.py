import streamlit as st
import pandas as pd
import requests

# Google Sheets маълумотларини ўқиш учун линк
БАЗА_URL = "https://docs.google.com/spreadsheets/d/1XyO5EqqDonEfQnmqr8j7SQNbVcx2SC93txhFVHoDGQA/export?format=csv"

# РАСМДАГИ УША КЎК ЛИНКНИ ШУ ЕРГА ҚЎЙИНГ:
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbz3Gk37aag317WPVwDaZTBCLr-ylpddGK7WR_10vYKkYF8luaN73NBOjHls6U5cvmq/exec"

def маълумотларни_юклаш():
    try:
        # Жадвални юклаш ва устун номларини тозалаш
        df = pd.read_csv(БАЗА_URL)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

def кириш_ойнаси():
    st.markdown('<div style="text-align: center; color: white;"><h1>🏥 MEDEXTRA Тизими</h1></div>', unsafe_allow_html=True)
    б1, б2 = st.tabs(["🔑 Кириш", "📝 Рўйхатдан ўтиш"])
    
    with б1:
        тел = st.text_input("Логин (Телефон)", key="l_u")
        парол = st.text_input("Пароль", type="password", key="l_p")
        if st.button("КИРИШ", use_container_width=True):
            база = маълумотларни_юклаш()
            if not база.empty:
                # Телефон устунини қидириш
                p_col = 'phone' if 'phone' in база.columns else база.columns[0]
                қидирув = база[база[p_col].astype(str) == str(тел)]
                
                if not қидирув.empty:
                    # Пароль ва статус устунлари
                    pass_col = 'password' if 'password' in база.columns else база.columns[1]
                    stat_col = 'status' if 'status' in база.columns else база.columns[-1]
                    
                    if str(қидирув.iloc[0][pass_col]) == str(парол):
                        статус = int(қидирув.iloc[0][stat_col])
                        if статус > 0:
                            st.session_state["auth"] = True
                            st.session_state["role"] = статус
                            st.session_state["user"] = қидирув.iloc[0].get('name', 'User')
                            st.rerun()
                        else:
                            st.warning("⚠️ Сўровингиз ҳали тасдиқланмаган.")
                    else:
                        st.error("❌ Пароль хато!")
                else:
                    st.error("❌ Бундай фойдаланувчи топилмади!")

    with б2:
        st.subheader("📝 Рўйхатдан ўтиш учун сўров")
        исм = st.text_input("Исм шарифингиз", key="r_n")
        номер = st.text_input("Телефон рақамингиз", key="r_p")
        янги_парол = st.text_input("Пароль танланг", key="r_pass")
        
        if st.button("СЎРОВ ЮБОРИШ", use_container_width=True):
            if исм and номер and янги_парол:
                payload = {"phone": номер, "password": янги_парол, "name": исм}
                try:
                    # Маълумотни Apps Script орқали жадвалга юбориш
                    res = requests.post(WEB_APP_URL, json=payload)
                    if res.status_code == 200:
                        st.success("✅ Сўров юборилди! Энди Панелда кўринади.")
                    else:
                        st.error("Юборишда хатолик юз берди.")
                except:
                    st.error("Серверга уланишда хатолик.")
            else:
                st.warning("Илтимос, ҳамма майдонларни тўлдиринг!")
