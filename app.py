import streamlit as st
import pandas as pd
import io
import zipfile
import re
import math

# 1. ДИЗАЙН ВА ФОН (ОНЛАЙН РАСМ БИЛАН)
st.set_page_config(page_title="MEDEXTRA", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1587854692152-cbe660feec90?q=80&w=2070");
        background-size: cover;
        background-attachment: fixed;
    }
    .main-block {
        background: rgba(0, 0, 0, 0.85);
        padding: 30px;
        border-radius: 15px;
        color: white;
        border: 1px solid #27AE60;
    }
    .footer {
        position: fixed;
        left: 0; bottom: 0; width: 100%;
        background-color: rgba(0, 0, 0, 0.8);
        color: white; text-align: center;
        padding: 10px; font-size: 16px;
    }
    </style>
    <div class="footer">Bog'lanish uchun: +998887549896</div>
    """, unsafe_allow_html=True)

# 2. МАНТИҚИЙ ФУНКЦИЯЛАР (ШУ ЕРНИНГ ЎЗИДА)
def get_pack_size(name):
    match = re.search(r'[N№](\d+)', str(name).upper())
    return int(match.group(1)) if match else 1

def calculate_logic(cost, mode, user_markup, pack_size):
    if cost <= 0: return 0, 0
    if mode == "admin":
        markup = 1.08 if cost >= 300000 else 1.10
    else:
        markup = 1 + (user_markup / 100)
    
    pachka_raw = cost * markup
    pachka_final = math.ceil(pachka_raw / 100) * 100
    dona_final = math.ceil((pachka_final / pack_size) / 100) * 100
    return int(pachka_final), int(dona_final)

# 3. КИРИШ ТИЗИМИ
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None

if not st.session_state.logged_in:
    st.markdown('<div class="main-block">', unsafe_allow_html=True)
    st.title("💊 MEDEXTRA: Tizimga Kirish")
    user = st.text_input("Login")
    pw = st.text_input("Parol", type="password")
    
    if st.button("Kirish"):
        if user == "admin" and pw == "Abbos96":
            st.session_state.logged_in = True
            st.session_state.user_role = "admin"
            st.rerun()
        elif user == "mijoz" and pw == "123":
            st.session_state.logged_in = True
            st.session_state.user_role = "mijoz"
            st.rerun()
        else:
            st.error("Login yoki parol xato!")
    st.markdown('</div>', unsafe_allow_html=True)

# 4. АСОСИЙ ИШЧИ ҚИСМ
else:
    st.sidebar.title(f"👤 {st.session_state.user_role}")
    if st.session_state.user_role == "admin":
        choice = st.sidebar.selectbox("Bo'lim:", ["Admin Hisob", "Mijoz Hisob"])
    else:
        choice = "Mijoz Hisob"

    st.markdown('<div class="main-block">', unsafe_allow_html=True)
    st.header(f"📊 {choice}")
    
    mode = "admin" if "Admin" in choice else "mijoz"
    user_markup = 10
    if mode == "mijoz":
        user_markup = st.select_slider("Ustama foizini tanlang (%)", 1, 20, 10)

    files = st.file_uploader("Excel fayllarni tanlang", accept_multiple_files=True)
    
    if files:
        results = {}
        for f in files:
            df = pd.read_excel(f)
            st.write(f"📁 **Fayl: {f.name}**")
            
            c1, c2 = st.columns(2)
            name_col = c1.selectbox(f"Dori nomi ({f.name}):", df.columns, key=f"n_{f.name}")
            cost_col = c2.selectbox(f"Tannarxi ({f.name}):", df.columns, index=min(3, len(df.columns)-1), key=f"c_{f.name}")
            
            if st.button(f"Hisoblash: {f.name}"):
                p_list, d_list = [], []
                for _, row in df.iterrows():
                    try:
                        cost_val = str(row[cost_col]).replace(' ','').replace(',','.')
                        cost = float(re.sub(r'[^\d.]', '', cost_val))
                    except: cost = 0
                    
                    size = get_pack_size(row[name_col])
                    p, d = calculate_logic(cost, mode, user_markup, size)
                    p_list.append(p); d_list.append(d)
                
                df['Pachka Sotuv (H)'] = p_list
                df['Dona Narxi (I)'] = d_list
                
                out = io.BytesIO()
                df.to_excel(out, index=False)
                results[f.name] = out.getvalue()
                st.success(f"{f.name} hisoblandi!")

        if results:
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, "w") as z:
                for name, data in results.items():
                    z.writestr(name, data)
            
            st.download_button("📥 Barcha fayllarni (ZIP) yuklab olish", zip_buf.getvalue(), "natija.zip", "application/zip")
    
    if st.sidebar.button("Chiqish"):
        st.session_state.logged_in = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
