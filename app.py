import streamlit as st
import pandas as pd
import io
import re
import math

# 1. САҲИФА СОЗЛАМАЛАРИ
st.set_page_config(page_title="MEDEXTRA", page_icon="💊", layout="centered")

# 2. МАТЕМАТИК ФУНКЦИЯЛАР (СИЗНИНГ ЖАДВАЛИНГИЗ АСОСИДА)
def get_pack_size(name):
    # Ном ичидан N30, №10 каби сонларни қидириш
    match = re.search(r'[N№](\d+)', str(name).upper())
    if match:
        return int(match.group(1))
    # Агар N йўқ бўлса, ном ичидаги оддий сонни қидириш (масалан: "5 талик")
    match_alt = re.search(r'(\d+)\s*(ТА|TA|ШТ|шт)', str(name).upper())
    if match_alt:
        return int(match_alt.group(1))
    return 1

def calculate_prices(cost, pack_size):
    # 1. Биринчи битта донасининг таннархини топамиз
    unit_cost = cost / pack_size
    
    # 2. Донасига 12% устама қўшиб, юзликка ТЕПАГА қараб яхлитлаймиз
    # Масалан: 2 249 + 12% = 2 518 -> 2 600 сўм
    dona_final = math.ceil((unit_cost * 1.12) / 100) * 100
    
    # 3. Пачка нархини яхлитланган дона нархидан келиб чиқиб ҳисоблаймиз
    # Бунда: 2 600 * 1 = 2 600 ёки 2 700 * 30 = 81 000
    pachka_final = dona_final * pack_size
    
    # 4. Ҳақиқий фоизни текшириш учун (Наценка устуни учун)
    real_markup = ((pachka_final / cost) - 1) * 100 if cost > 0 else 0
    
    return pachka_final, dona_final, real_markup

# 3. ДИЗАЙН (АВВАЛГИ ВАРИАНТ УЗГАРМАГАН)
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
        .blue-label {{
            background-color: #004a99;
            color: white !important;
            padding: 5px 15px;
            border-radius: 5px;
            display: inline-block;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .stButton>button {{
            background-color: #004a99 !important;
            color: white !important;
            border-radius: 10px !important;
            font-weight: bold !important;
            height: 3em !important;
        }}
        .footer-box {{
            background-color: #004a99;
            color: white !important;
            padding: 10px;
            border-radius: 5px;
            margin-top: 20px;
            text-align: center;
        }}
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

# 4. ЛОГИН ТИЗИМИ (admin / Abbos96)
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
            if user_input == "admin" and password_input == "Abbos96":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ Логин ёки парол хато!")
        
        st.markdown(f'<div class="footer-box">Боғланиш: <br><b>📞 +998 88 754 98 96</b></div>', unsafe_allow_html=True)
    st.stop()

# 5. АСОСИЙ ИШЧИ КИСМ
st.markdown("<h1 style='color: white; text-shadow: 2px 2px 8px black; text-align: center;'>📋 Файлларни ҳисоблаш</h1>", unsafe_allow_html=True)

uploaded_files = st.file_uploader("📂 Excel файлни танланг", type=['xlsx'], accept_multiple_files=True)

if uploaded_files:
    for i, file in enumerate(uploaded_files):
        with st.expander(f"📄 {file.name}"):
            df = pd.read_excel(file)
            cols = df.columns.tolist()
            
            c1, c2 = st.columns(2)
            col_name = c1.selectbox(f"Дори номи устуни", cols, key=f"n_{i}")
            col_cost = c2.selectbox(f"Таннарх устуни", cols, index=min(3, len(cols)-1), key=f"c_{i}")
            
            if st.button(f"🚀 Ҳисоблаш", key=f"b_{i}"):
                p_list, d_list, m_list = [], [], []
                for _, row in df.iterrows():
                    try:
                        # Таннархни форматлаш (пробел ва вергулларни тўғирлаш)
                        val = str(row[col_cost]).replace(' ', '').replace(',', '.')
                        cost = float(re.sub(r'[^\d.]', '', val))
                        
                        # Сонини аниқлаш
                        size = get_pack_size(row[col_name])
                        
                        # ҲИСОБЛАШ
                        p_p, d_p, m_p = calculate_prices(cost, size)
                        
                        p_list.append(p_p)
                        d_list.append(d_p)
                        m_list.append(f"{m_p:.2f}%")
                    except:
                        p_list.append(0); d_list.append(0); m_list.append("0%")
                
                df['Наценка (Фоиз)'] = m_list
                df['Pachka Sotuv'] = p_list
                df['Dona Narxi'] = d_list
                
                st.success("✅ Сизнинг жадвалингиз асосида ҳисобланди!")
                st.dataframe(df[['Pachka Sotuv', 'Dona Narxi', 'Наценка (Фоиз)']].head(10))
                
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False)
                st.download_button("📥 Натижани юклаш", output.getvalue(), f"Tayyor_{file.name}", key=f"d_{i}")
