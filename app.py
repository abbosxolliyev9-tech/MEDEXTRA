import streamlit as st
import pandas as pd
import io
import zipfile
import re
import math

# 1. ДИЗАЙН ВА ФОН
st.set_page_config(page_title="MEDEXTRA", layout="wide")

# Орқа фон расмини қайтариш ва стиллар
st.markdown("""
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/pexels-eren-34577902.jpg");
        background-size: cover;
        background-attachment: fixed;
    }
    .main-block {
        background: rgba(0, 0, 0, 0.85);
        padding: 30px;
        border-radius: 15px;
        color: white;
        border: 1px solid #27AE60;
        margin-bottom: 50px;
    }
    .stButton>button {
        width: 100%;
        background-color: #27AE60 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 10px !important;
    }
    .footer {
        position: fixed;
        left: 0; bottom: 0; width: 100%;
        background-color: rgba(0, 0, 0, 0.9);
        color: white; text-align: center;
        padding: 10px; font-size: 16px;
        z-index: 1000;
    }
    </style>
    <div class="footer">Bog'lanish uchun: +998887549896</div>
    """, unsafe_allow_html=True)

# 2. МАНТИҚИЙ ФУНКЦИЯЛАР
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

    # Файлларни юклаш
    files = st.file_uploader("Excel fayllarni tanlang (Bir nechta)", accept_multiple_files=True)
    
    if files:
        st.info(f"Юкланган файллар сони: {len(files)}")
        
        # Ҳар бир файл учун устунларни текшириш учун вақтинчалик рўйхат
        all_data_ready = True
        file_configs = {}

        for f in files:
            # Сарлавҳаларни ўқиб олиш
            df_temp = pd.read_excel(f, nrows=0)
            cols = df_temp.columns.tolist()
            
            st.write(f"⚙️ **Настройка: {f.name}**")
            col_a, col_b = st.columns(2)
            
            with col_a:
                n_col = st.selectbox(f"Dori nomi ({f.name})", cols, key=f"n_{f.name}")
            with col_b:
                # Нарх устунини автоматик топишга ҳаракат (одатда 4-устун)
                default_idx = min(3, len(cols)-1)
                c_col = st.selectbox(f"Tannarxi ({f.name})", cols, index=default_idx, key=f"c_{f.name}")
            
            file_configs[f.name] = {"n": n_col, "c": c_col}
            st.markdown("---")

        # ЯГОНА ҲИСОБЛАШ ТУГМАСИ
        if st.button("🚀 БАРЧА ФАЙЛЛАРНИ БАРАВАРИГА ҲИСОБЛАШ"):
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                progress_bar = st.progress(0)
                for i, f in enumerate(files):
                    # Файлни тўлиқ ўқиш
                    df = pd.read_excel(f)
                    config = file_configs[f.name]
                    
                    p_list, d_list = [], []
                    for _, row in df.iterrows():
                        try:
                            # Нархни тозалаш
                            cost_raw = str(row[config['c']]).replace(' ','').replace(',','.')
                            cost = float(re.sub(r'[^\d.]', '', cost_raw))
                        except:
                            cost = 0
                        
                        size = get_pack_size(row[config['n']])
                        p, d = calculate_logic(cost, mode, user_markup, size)
                        p_list.append(p)
                        d_list.append(d)
                    
                    df['Pachka Sotuv (H)'] = p_list
                    df['Dona Narxi (I)'] = d_list
                    
                    # Excelни хотирада яратиш
                    output = io.BytesIO()
                    df.to_excel(output, index=False)
                    
                    # ZIP ичига қўшиш
                    zf.writestr(f.name, output.getvalue())
                    progress_bar.progress((i + 1) / len(files))
                
            st.success("✅ Барча файллар муваффақиятли ҳисобланди!")
            
            # ZIPни юклаб олиш тугмаси
            st.download_button(
                label="📥 Тайёр ZIP архивни юклаб олиш",
                data=zip_buffer.getvalue(),
                file_name="medextra_natijalar.zip",
                mime="application/zip"
            )
            
    if st.sidebar.button("Chiqish"):
        st.session_state.logged_in = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
