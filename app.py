import streamlit as st
import pandas as pd
import io
import zipfile
import re
import math

# 1. ДИЗАЙН
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
        background-color: rgba(0, 0, 0, 0.9);
        color: white; text-align: center;
        padding: 10px; font-size: 16px;
    }
    </style>
    <div class="footer">Bog'lanish uchun: +998887549896</div>
    """, unsafe_allow_html=True)

# 2. МАНТИҚ: ДОИМ ПАСТГА ЯХЛИТЛАШ (Агар 9% дан кам бўлмаса)
def get_pack_size(name):
    match = re.search(r'[N№](\d+)', str(name).upper())
    return int(match.group(1)) if match else 1

def calculate_logic(cost, mode, user_markup, pack_size):
    if cost <= 0: return 0, 0
    
    # 1. Аввал стандарт устамани ҳисоблаймиз (Админ: 10% ёки 8%, Мижоз: танланган %)
    if mode == "admin":
        target_markup = 1.10 if cost < 300000 else 1.08
    else:
        target_markup = 1 + (user_markup / 100)
    
    # Хом нарх (масалан: 10,120 ёки 10,800)
    raw_price = cost * target_markup
    
    # 2. Энг яқин пастки МИНГЛИККА яхлитлаймиз (Масалан: 10,120 -> 10,000 ёки 10,900 -> 10,000)
    lower_thousand = (raw_price // 1000) * 1000
    
    # 3. ТЕКШИРУВ: Агар пастга туширилган нарх таннархдан камида 9% баланд бўлса:
    if lower_thousand >= (cost * 1.09):
        pachka_final = lower_thousand
    else:
        # Агар 9% дан камайиб кетса, унда тепага 100 сўмгача яхлитлаймиз
        pachka_final = math.ceil(raw_price / 100) * 100
    
    # Дона нархи учун ҳам худди шу мантиқ
    dona_raw = pachka_final / pack_size
    dona_lower_thousand = (dona_raw // 1000) * 1000
    
    if dona_lower_thousand >= ((cost / pack_size) * 1.09):
        dona_final = dona_lower_thousand
    else:
        dona_final = math.ceil(dona_raw / 100) * 100
        
    return int(pachka_final), int(dona_final)

# 3. КИРИШ ТИЗИМИ
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<div class="main-block">', unsafe_allow_html=True)
    st.title("💊 MEDEXTRA: Tizimga Kirish")
    user = st.text_input("Login")
    pw = st.text_input("Parol", type="password")
    if st.button("Kirish"):
        if (user == "admin" and pw == "Abbos96") or (user == "mijoz" and pw == "123"):
            st.session_state.logged_in = True
            st.session_state.user_role = user
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# 4. ФАЙЛЛАР БИЛАН ИШЛАШ (ZIP)
else:
    st.sidebar.title(f"👤 {st.session_state.user_role}")
    choice = st.sidebar.selectbox("Bo'lim:", ["Admin Hisob", "Mijoz Hisob"]) if st.session_state.user_role == "admin" else "Mijoz Hisob"
    
    st.markdown('<div class="main-block">', unsafe_allow_html=True)
    mode = "admin" if "Admin" in choice else "mijoz"
    user_markup = st.select_slider("Mijoz Ustama %", 1, 20, 10) if mode == "mijoz" else 10

    files = st.file_uploader("Excel fayllarni tanlang", accept_multiple_files=True)
    
    if files:
        configs = {}
        for f in files:
            df_cols = pd.read_excel(f, nrows=0).columns.tolist()
            st.write(f"📁 {f.name}")
            c1, c2 = st.columns(2)
            n = c1.selectbox(f"Dori nomi", df_cols, key=f"n_{f.name}")
            c = c2.selectbox(f"Tannarxi", df_cols, index=min(3, len(df_cols)-1), key=f"c_{f.name}")
            configs[f.name] = {"n": n, "c": c}

        if st.button("🚀 БАРЧА ФАЙЛЛАРНИ ҲИСОБЛАШ ВА ZIP ЮКЛАШ"):
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
                        p, d = calculate_logic(cost, mode, user_markup, get_pack_size(row[cfg['n']]))
                        p_res.append(p); d_res.append(d)
                    
                    df['Sotuv Narxi (H)'] = p_res
                    df['Dona Narxi (I)'] = d_res
                    
                    output = io.BytesIO()
                    df.to_excel(output, index=False)
                    zf.writestr(f.name, output.getvalue())
            
            st.success("Ҳисоблаш тугади!")
            st.download_button("📥 ZIP файлни юклаб олиш", zip_buf.getvalue(), "medextra_results.zip")
    
    if st.sidebar.button("Chiqish"):
        st.session_state.logged_in = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
