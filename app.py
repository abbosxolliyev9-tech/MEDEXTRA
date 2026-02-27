import streamlit as st
import pandas as pd
import io
import re
import math

# 1. САҲИФА СОЗЛАМАЛАРИ
st.set_page_config(page_title="MEDEXTRA", page_icon="💊", layout="wide")

# 2. МАТЕМАТИК ФУНКЦИЯЛАР (Биринчи шулар туриши шарт, акс ҳолда NameError беради)
def get_pack_size(name):
    """Дори номидан N ёки № белгиси орқали сонини топади"""
    match = re.search(r'[N№](\d+)', str(name).upper())
    return int(match.group(1)) if match else 1

def calculate_prices(cost, pack_size):
    """Насиб қилса, баракали нарх ҳисоблаш формуласи"""
    pachka_final = math.ceil((cost * 1.12) / 100) * 100
    dona_final = math.ceil((pachka_final / (pack_size if pack_size > 0 else 1)) / 100) * 100
    return pachka_final, dona_final

# 3. ДИЗАЙН (CSS) - Янги расм ва оқ блок учун
def add_custom_style():
    # Сиз юклаган янги расм линки
    bg_image_url = "https://raw.githubusercontent.com/abbosxolliyev9-tech/MEDEXTRA/main/pexels-eren-34577902.jpg"
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{bg_image_url}");
            background-attachment: fixed;
            background-size: cover;
            background-position: center;
        }}
        .login-card {{
            background-color: rgba(255, 255, 255, 0.98);
            padding: 45px;
            border-radius: 20px;
            box-shadow: 0px 15px 35px rgba(0,0,0,0.5);
            max-width: 450px;
            margin: auto;
            text-align: center;
            border: 1px solid #ddd;
        }}
        .stTextInput label {{
            color: #1a1a1a !important;
            font-weight: bold !important;
        }}
        .stButton>button {{
            background-color: #004a99 !important;
            color: white !important;
            border-radius: 10px !important;
            height: 3.5em !important;
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
        col1, col2, col3 = st.columns([1, 1.3, 1])
        with col2:
            st.markdown('<div class="login-card">', unsafe_allow_html=True)
            st.markdown("<h1 style='color: #004a99; margin-bottom: 0;'>💊 MEDEXTRA</h1>", unsafe_allow_html=True)
            st.markdown("<p style='color: #555; margin-bottom: 25px;'>Фармацевтика тизими</p>", unsafe_allow_html=True)
            st.text_input("Логин", key="user")
            st.text_input("Парол", type="password", key="password")
            st.button("ТИЗИМГА КИРИШ", use_container_width=True, on_click=password_entered)
            if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                st.error("❌ Логин ёки парол хато!")
            st.markdown('</div>', unsafe_allow_html=True)
        return False
    return True

# 5. АСОСИЙ ИШЧИ ҚИСМ (Фақат логиндан ўтгач ишлайди)
if check_password():
    with st.sidebar:
        st.markdown("### 👨‍💼 Админ Панели")
        if st.button("🚪 Тизимдан чиқиш"):
            st.session_state.clear()
            st.rerun()

    st.markdown("<h1 style='color: white; text-shadow: 3px 3px 10px black; text-align: center;'>📋 Кўп сонли файлларни ҳисоблаш</h1>", unsafe_allow_html=True)

    # БИР НЕЧТА ФАЙЛНИ ЮКЛАШ (accept_multiple_files=True)
    uploaded_files = st.file_uploader("📂 Excel (.xlsx) файлларини танланг", type=['xlsx'], accept_multiple_files=True)

    if uploaded_files:
        for i, file in enumerate(uploaded_files):
            # Ҳар бир файл учун алоҳида блок
            with st.expander(f"📄 Файл: {file.name}", expanded=True):
                df = pd.read_excel(file)
                cols = df.columns.tolist()
                
                c1, c2 = st.columns(2)
                with c1:
                    col_name = st.selectbox(f"Дори номи устуни ({file.name}):", cols, index=0, key=f"n_{i}")
                with c2:
                    col_cost = st.selectbox(f"Таннарх устуни ({file.name}):", cols, index=min(3, len(cols)-1), key=f"c_{i}")
                
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
                    
                    st.success(f"✅ {file.name} муваффақиятли ҳисобланди!")
                    st.dataframe(df.head(10)) 
                    
                    # Натижани юклаб олиш
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False)
                    st.download_button(
                        label=f"📥 {file.name} натижасини юклаш",
                        data=output.getvalue(),
                        file_name=f"HISOBLANGAN_{file.name}",
                        key=f"dl_{i}",
                        use_container_width=True
                    )
