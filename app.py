import streamlit as st
import pandas as pd
import io
import zipfile
import re
from calculations.logic import get_pack_size, calculate_logic
from tizim.auth import login_system, apply_design

# Дизайнни қўллаш
apply_design()
login_system()

if st.session_state.get('logged_in'):
    st.sidebar.title(f"👤 {st.session_state.user_role}")
    
    # Меню
    if st.session_state.user_role == "admin":
        choice = st.sidebar.selectbox("Bo'lim:", ["Admin Hisob", "Mijoz Hisob"])
    else:
        choice = "Mijoz Hisob"

    st.markdown('<div class="main-block">', unsafe_allow_html=True)
    st.header(f"📊 {choice}")
    
    mode = "admin" if "Admin" in choice else "mijoz"
    markup = 10
    if mode == "mijoz":
        markup = st.select_slider("Ustama %", 1, 20, 10)

    # Файлларни юклаш
    files = st.file_uploader("Excel fayllarni tanlang", accept_multiple_files=True)
    
    if files:
        results = {}
        for f in files:
            df = pd.read_excel(f)
            st.write(f"📁 **{f.name}**")
            
            c1, c2 = st.columns(2)
            name_col = c1.selectbox(f"Nomi:", df.columns, key=f"n_{f.name}")
            cost_col = c2.selectbox(f"Tannarxi:", df.columns, index=min(3, len(df.columns)-1), key=f"c_{f.name}")
            
            if st.button(f"Hisobla: {f.name}"):
                p_list, d_list = [], []
                for _, row in df.iterrows():
                    try:
                        cost_val = str(row[cost_col]).replace(' ','').replace(',','.')
                        cost = float(re.sub(r'[^\d.]', '', cost_val))
                    except: cost = 0
                    
                    size = get_pack_size(row[name_col])
                    p, d = calculate_logic(cost, mode, markup, size)
                    p_list.append(p); d_list.append(d)
                
                df['Sotuv (H)'] = p_list
                df['Dona (I)'] = d_list
                
                out = io.BytesIO()
                df.to_excel(out, index=False)
                results[f.name] = out.getvalue()
                st.success(f"{f.name} tayyor!")

        if results:
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, "w") as z:
                for name, data in results.items():
                    z.writestr(name, data)
            
            st.download_button("📥 ZIP-ни юклаш", zip_buf.getvalue(), "hisob.zip", "application/zip")
    
    if st.sidebar.button("Chiqish"):
        st.session_state.logged_in = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    elif choice == "Админ Панель":
        st.write("🌐 Google Sheets: [Ochish](https://docs.google.com/spreadsheets/d/1XyO5EqqDonEfQnmqr8j7SQNbVcx2SC93txhFVHoDGQA/edit)")

    st.markdown('</div>', unsafe_allow_html=True)
