import streamlit as st
import pandas as pd
import io
import zipfile
import re
import math

# 1. ДИЗАЙН ВА САҲИФА
st.set_page_config(page_title="MEDEXTRA", layout="wide")

st.markdown("""
    <style>
    .stApp { background-image: url("https://images.unsplash.com/photo-1587854692152-cbe660feec90?q=80&w=2070"); background-size: cover; background-attachment: fixed; }
    .main-block { background: rgba(0, 0, 0, 0.88); padding: 30px; border-radius: 15px; color: white; border: 1px solid #27AE60; }
    .stButton>button { width: 100%; background-color: #27AE60 !important; color: white !important; font-weight: bold !important; height: 3.5em; border-radius: 10px !important; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: rgba(0, 0, 0, 0.95); color: white; text-align: center; padding: 10px; border-top: 1px solid #27AE60; }
    </style>
    <div class="footer">Bog'lanish: +998887549896</div>
    """, unsafe_allow_html=True)

# 2. МАНТИҚ: 1000 ВА 500 ГА ЯХЛИТЛАШ (ТИЙИНСИЗ)
def get_pack_size(name):
    match = re.search(r'[N№](\d+)', str(name).upper())
    return int(match.group(1)) if match else 1

def calculate_logic(cost, mode, user_markup, pack_size):
    if cost <= 0: return 0, 0
    
    # 1. Асосий фоизларни белгилаш
    if mode == "admin":
        target_markup = 1.08 if cost >= 300000 else 1.10
    else:
        target_markup = 1 + (user_markup / 100)
    
    # Хом нарх
    raw_pachka = cost * target_markup
    
    # 2. ПАЧКА НАРХИНИ ЯХЛИТЛАШ (1000 гача)
    # Аввал пастга мингликка яхлитлаб кўрамиз (Масалан: 23 400 -> 23 000)
    p_down_1000 = (raw_pachka // 1000) * 1000
    if p_down_1000 >= (cost * 1.09):
        pachka_final = int(p_down_1000)
    else:
        # Агар 9% дан паст бўлса, 500 га яхлитлаймиз
        p_down_500 = (raw_pachka // 500) * 500
        if p_down_500 >= (cost * 1.09):
            pachka_final = int(p_down_500)
        else:
            # Агар яна паст бўлса, тепага 500 га яхлитлаймиз
            pachka_final = int(math.ceil(raw_pachka / 500) * 500)

    # 3. ДОНА НАРХИНИ ЯХЛИТЛАШ (Тийинсиз, 1000 ёки 500 га)
    dona_raw = pachka_final / pack_size
    d_down_1000 = (dona_raw // 1000) * 1000
    
    if d_down_1000 >= ((cost / pack_size) * 1.09):
        dona_final = int(d_down_1000)
    else:
        d_down_500 = (dona_raw // 500) * 500
        if d_down_500 >= ((cost / pack_size) * 1.09):
            dona_final = int(d_down_500)
        else:
            dona_final = int(math.ceil(dona_raw / 100) * 100) # Донада 100 гача тепага яхлитлаш (кам ҳолларда)

    return pachka_final, dona_final

# 3. КИРИШ ВА ИШЧИ ҚИСМ
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<div class="main-block">', unsafe_allow_html=True)
    st.title("💊 MEDEXTRA: Kirish")
    u, p = st.text_input("Login"), st.text_input("Parol", type="password")
    if st.button("Kirish"):
        if (u == "admin" and p == "Abbos96") or (u == "mijoz" and p == "123"):
            st.session_state.logged_in, st.session_state.user_role = True, u
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.sidebar.title(f"👤 {st.session_state.user_role}")
    mode_choice = st.sidebar.selectbox("Bo'lim:", ["Admin", "Mijoz"]) if st.session_state.user_role == "admin" else "Mijoz"
    
    st.markdown('<div class="main-block">', unsafe_allow_html=True)
    user_markup = st.select_slider("Mijoz %", 1, 20, 10) if mode_choice == "Mijoz" else 10

    files = st.file_uploader("Excel fayllar", accept_multiple_files=True)
    if files:
        configs = {}
        for f in files:
            cols = pd.read_excel(f, nrows=0).columns.tolist()
            st.write(f"⚙️ {f.name}")
            c1, c2 = st.columns(2)
            configs[f.name] = {"n": c1.selectbox("Nomi", cols, key=f"n_{f.name}"), 
                               "c": c2.selectbox("Tannarxi", cols, index=min(3, len(cols)-1), key=f"c_{f.name}")}

        if st.button("🚀 ХИСОБЛАШ ВА ZIP ЮКЛАШ"):
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, "w") as zf:
                for f in files:
                    df = pd.read_excel(f)
                    cfg = configs[f.name]
                    p_res, d_res = [], []
                    for _, row in df.iterrows():
                        try:
                            val = str(row[cfg['c']]).replace(' ','').replace(',','.')
                            cost = float(re.sub(r'[^\d.]', '', val))
                        except: cost = 0
                        p, d = calculate_logic(cost, mode_choice.lower(), user_markup, get_pack_size(row[cfg['n']]))
                        p_res.append(p); d_res.append(d)
                    
                    df['Sotuv_Pachka'] = p_res
                    df['Sotuv_Dona'] = d_res
                    out = io.BytesIO()
                    df.to_excel(out, index=False)
                    zf.writestr(f"Tayyor_{f.name}", out.getvalue())
            
            st.success("Tayyor!")
            st.download_button("📥 ZIP юклаш", zip_buf.getvalue(), "medextra.zip")
    st.markdown('</div>', unsafe_allow_html=True)
