elif menu == "⚙️ Панел":
    st.markdown('<div class="blue-label">⚙️ БОШҚАРУВ ПАНЕЛИ</div>', unsafe_allow_html=True)
    
    # 1. Google Sheets-га ўтиш тугмаси
    sheet_link = "https://docs.google.com/spreadsheets/d/1XyO5EqqDonEfQnmqr8j7SQNbVcx2SC93txhFVHoDGQA/edit"
    st.link_button("📂 Google Sheets Жадвалини Очиш", sheet_link, use_container_width=True)
    
    st.divider()
    
    # 2. Тасдиқлашни кутаётганлар (status == 0 бўлганлар)
    база = маълумотларни_юклаш()
    янгилар = база[база['status'] == 0]
    
    st.subheader(f"🔔 Тасдиқ кутаётган сўровлар: {len(янгилар)}")
    
    if not янгилар.empty:
        for i, row in янгилар.iterrows():
            with st.expander(f"👤 {row['name']} ({row['phone']})"):
                c1, c2 = st.columns(2)
                if c1.button(f"✅ Тасдиқлаш", key=f"ok_{i}"):
                    st.info(f"Жадвалда {row['name']} нинг статусини 1 қилиб ўзгартиринг.")
                if c2.button(f"❌ Рад этиш", key=f"no_{i}"):
                    st.warning("Жадвалдан ушбу қаторни ўчириб ташланг.")
    else:
        st.write("Ҳозирча янги сўровлар йўқ.")

    # 3. Барча ходимлар рўйхати
    st.divider()
    st.subheader("👥 Барча фойдаланувчилар")
    st.dataframe(база[['name', 'phone', 'status']], use_container_width=True)

st.sidebar.markdown(f"👤: {st.session_state['user']}")
