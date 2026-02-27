import streamlit as st
import pandas as pd
import io
import re
import math

# 1. Саҳифа созламалари
st.set_page_config(page_title="MEDEXTRA", page_icon="💊", layout="centered")

# 2. Математик функциялар
def get_pack_size(name):
    match = re.search(r'[N№](\d+)', str(name).upper())
    return int(match.group(1)) if match else 1

def calculate_prices(cost, pack_size):
    pachka_final = math.ceil((cost * 1.12) / 100) * 100
    dona_final = math.ceil((pachka_final / (pack_size if pack_size > 0 else 1)) / 100) * 100
    return pachka_final, dona_final

# 3. ДИЗАЙН (CSS) - Кўк фонли стиллар
def add_custom_style():
    bg_image_url = "https://raw.githubusercontent.com/abbosxolliyev9-tech/MEDEXTRA/main/pexels-eren-34577902.jpg"
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{bg_image_url}");
            background-size: cover;
            background-position: center;
        }}
        
        /* Кўк фонли лейбллар */
        .blue-label {{
            background-color: #004a99;
            color: white !important;
            padding: 5px 15px;
            border-radius: 5px;
            display: inline-block;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        /* Кириш тугмаси */
        .stButton>button {{
            background-color: #004a99 !important;
            color: white !important;
            border-radius: 10px !important;
            font-weight: bold !important;
            height: 3em !important;
        }}

        /* Пастки кўк блок */
        .footer-box {{
            background-color: #004a99;
            color: white !important;
            padding: 10px;
            border-radius: 5px;
            margin-top: 20px;
            text-align: center;
        }}
        
        /* Input устидаги ёзувлар */
        .stTextInput label {{
            background-color: #004a99 !important;
            color: white !important;
            padding: 2px 10px !important;
            border-radius: 3px !important;
        }}
        </style>
        """, 
        unsafe_allow_html=True
    )

add_custom_style()

# 4. ЛОГИН ТИЗИМИ (Янгиланган логин ва парол)
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    col1, col2, col3 = st.columns([0.1, 1, 0.1])
    with col2:
        st.write("<br><br>", unsafe_allow_html=True)
        
        st.markdown('<div class="blue-label" style="font-size: 30px;">💊 MEDEXTRA</div>', unsafe_allow_html=True)
        st.markdown('<br><div class="blue-label">Фармацевтика тизимига кириш</div>', unsafe_allow_html=True)
        
        user_input = st.text_input("Логин", placeholder="admin")
        password_input = st.text_input("Парол", type="password", placeholder="****")
        
        if st.button("ТИЗИМГА КИРИШ", use_container_width=True):
            # ШУ ЕРДА ЯНГИ ПАРОЛ ЎРНАТИЛДИ
            if user_input == "admin" and password_input == "Abbos96":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ Логин ёки парол хато!")
        
        st.markdown(
            """
            <div class="footer-box">
                Ушбу тизимдан фойдаланиш учун биз билан боғланинг:<br>
                <span style="font-size: 18px;">📞 +998 88 754 98 96</span>
            </div>
            """, 
            unsafe_allow_html=True
        )
    st.stop()

# 5. АСОСИЙ ИШЧИ ПАНЕЛЬ
if st.sidebar.button("🚪 Чиқиш"):
    st.session_state["password_correct"] = False
    st.rerun()

st.markdown("<h1 style='color: white; text-shadow: 2px 2px 8px black; text-align: center;'>📋 Ҳисоб-китоб панели</h1>", unsafe_allow_html=True)

uploaded_files = st.file_uploader("📂 Excel файлларни юкланг", type=['xlsx'], accept_multiple_files=True)

if uploaded_files:
    for i, file in enumerate(uploaded_files):
        with st.expander(f"📄 {file.name}"):
            df = pd.read_excel(file)
            cols = df.columns.tolist()
            
            c1, c2 = st.columns(2)
            col_name = c1.selectbox(f"Номи", cols, key=f"n_{i}")
            col_cost = c2.selectbox(f"Таннарх", cols, index=min(3, len(cols)-1), key=f"c_{i}")
            
            if st.button(f"Ҳисоблаш", key=f"b_{i}"):
                p_list, d_list = [], []
                for _, row in df.iterrows():
                    try:
                        val = str(row[col_cost]).replace(' ', '').replace(',', '.')
                        cost = float(re.sub(r'[^\d.]', '', val))
                        size = get_pack_size(row[col_name])
                        p_p, d_p = calculate_prices(cost, size)
                        p_list.append(p_p)
                        d_list.append(d_p)
                    except:
                        p_list.append(0); d_list.append(0)
                
                df['Pachka Sotuv'] = p_list
                df['Dona Narxi'] = d_list
                st.success("Ҳисобланди!")
                st.dataframe(df.head())
                
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False)
                st.download_button("📥 Юклаб олиш", output.getvalue(), f"Tayyor_{file.name}", key=f"d_{i}")
