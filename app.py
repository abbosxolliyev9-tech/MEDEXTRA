import streamlit as st
import pandas as pd
import io
import re
import math

# 1. САҲИФА СОЗЛАМАЛАРИ
st.set_page_config(page_title="MEDEXTRA", page_icon="💊", layout="wide")

# 2. МАТЕМАТИК ФУНКЦИЯЛАР (NameError бермаслиги учун энг тепада)
def get_pack_size(name):
    match = re.search(r'[N№](\d+)', str(name).upper())
    return int(match.group(1)) if match else 1

def calculate_prices(cost, pack_size):
    pachka_final = math.ceil((cost * 1.12) / 100) * 100
    dona_final = math.ceil((pachka_final / (pack_size if pack_size > 0 else 1)) / 100) * 100
    return pachka_final, dona_final

# 3. ДИЗАЙН (CSS) - ҲАММА НАРСАНИ ОҚ БЛОК ИЧИГА ОЛИШ
def add_custom_style():
    # Орқа фон учун сиз танлаган тоғли манзара (pexels-eren-34577902.jpg)
    bg_image_url = "https://raw.githubusercontent.com/abbosxolliyev9-tech/MEDEXTRA/main/pexels-eren-34577902.jpg"
    st.markdown(
        f"""
        <style>
        /* Орқа фон созламаси */
        .stApp {{
            background-image: url("{bg_image_url}");
            background-attachment: fixed;
            background-size: cover;
            background-position: center;
        }}
        
        /* КИРИШ ОЙНАСИ (ОҚ ТЎРТБУРЧАК) */
        .login-card {{
            background-color: rgba(255, 255, 255, 0.98);
            padding: 40px;
            border-radius: 25px;
            box-shadow: 0px 20px 40px rgba(0,0,0,0.5);
            max-width: 450px;
            margin: auto;
            text-align: center;
            border: 1px solid #ddd;
        }}
        
        /* Логин ва Парол ёзувларини тўқ ва аниқ қилиш */
        .stTextInput label {{
            color: #1a1a1a !important;
            font-weight: bold !important;
            font-size: 16px !important;
            display: flex;
        }}
        
        /* Тугма дизайни */
        .stButton>button {{
            background-color: #004a99 !important;
            color: white !important;
            font-weight: bold !important;
            border-radius: 12px !important;
            height: 3.5em !important;
            margin-top: 20px;
        }}
        
        /* Боғланиш қисми учун стиль */
        .contact-box {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #444;
            font-size: 14px;
        }}
        </style>
        """, 
        unsafe_allow_html=True
    )

add_custom_style()

# 4. ЛОГИН ТИЗИМИ
def check_password():
    def password_entered():
        if st.session_state["password"] == "admin123" and st.session_state["user"] == "admin":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["user"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.write("<br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            # --- ОҚ ТЎРТБУРЧАК БОШЛАНИШИ ---
            st.markdown('<div class="login-card">', unsafe_allow_html=True)
            
            st.markdown("<h1 style='color: #004a99; margin-bottom: 0;'>💊 MEDEXTRA</h1>", unsafe_allow_html=True)
            st.markdown("<p style='color: #555; margin-bottom: 20px;'>Фармацевтика тизимига кириш</p>", unsafe_allow_html=True)
            
            st.text_input("Логин", key="user")
            st.text_input("Парол", type="password", key="password")
            
            st.button("ТИЗИМГА КИРИШ", use_container_width=True, on_click=password_entered)
            
            if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                st.error("❌ Логин ёки парол хато!")
            
            # Сиз сўраган боғланиш маълумоти (Оқ блок ичида)
            st.markdown(
                """
                <div class="contact-box">
                    Ушбу тизимдан фойдаланиш учун биз билан боғланинг:<br>
                    <b style="color: #004a99; font-size: 16px;">📞 +998 88 754 98 96</b>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
            # --- ОҚ ТЎРТБУРЧАК ТУГАШИ ---
            
        return False
    return True

# 5. АСОСИЙ ҚИСМ (Бир вақтда кўп файллар билан ишлаш)
if check_password():
    with st.sidebar:
        st.markdown("### 👨‍💼 Админ")
        if st.button("🚪 Чиқиш"):
            st.session_state.clear()
            st.rerun()

    st.markdown("<h1 style='color: white; text-shadow: 3px 3px 10px black; text-align: center;'>📋 Файлларни ҳисоблаш</h1>", unsafe_allow_html=True)

    uploaded_files = st.file_uploader("📂 Excel файлларини танланг", type=['xlsx'], accept_multiple_files=True)

    if uploaded_files:
        for i, file in enumerate(uploaded_files):
            with st.expander(f"📄 Файл: {file.name}", expanded=True):
                df = pd.read_excel(file)
                cols = df.columns.tolist()
                
                c1, c2 = st.columns(2)
                with c1:
                    col_name = st.selectbox(f"Дори номи ({file.name}):", cols, key=f"n_{i}")
                with c2:
                    col_cost = st.selectbox(f"Таннарх ({file.name}):", cols, index=min(3, len(cols)-1), key=f"c_{i}")
                
                if st.button(f"🚀 Ҳисоблаш: {file.name}", key=f"b_{i}"):
                    p_list, d_list = [], []
                    for _, row in df.iterrows():
                        try:
                            val = str(row[col_cost]).replace(' ', '').replace(',', '.')
                            cost = float(re.sub(r'[^\d.]', '', val))
                        except: cost = 0
                        
                        size = get_pack_size(row[col_name])
                        p_p, d_p = calculate_prices(cost, size)
                        p_list.append(p_p)
                        d_list.append(d_p)
                    
                    df['Pachka Sotuv (H)'] = p_list
                    df['Dona Narxi (I)'] = d_list
                    
                    st.success(f"✅ {file.name} ҳисобланди!")
                    st.dataframe(df.head(10)) 
                    
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False)
                    st.download_button(f"📥 Натижани юклаш", output.getvalue(), f"HISOBLANGAN_{file.name}", key=f"dl_{i}", use_container_width=True)
