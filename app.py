import streamlit as st
import pandas as pd
import io
import re
import math
import pdfplumber  # Yangi kutubxona

# 1. САҲИФА СОЗЛАМАЛАРИ
st.set_page_config(page_title="MEDEXTRA", page_icon="💊", layout="centered")

# 2. МАТЕМАТИК ФУНКЦИЯЛАР (СИЗНИНГ ЖАДВАЛИНГИЗ АСОСИДА)
def get_pack_size(name):
    match = re.search(r'[N№](\d+)', str(name).upper())
    if match:
        return int(match.group(1))
    match_alt = re.search(r'(\d+)\s*(ТА|TA|ШТ|шт)', str(name).upper())
    if match_alt:
        return int(match_alt.group(1))
    return 1

def calculate_prices(cost, pack_size):
    unit_cost = cost / pack_size
    dona_final = math.ceil((unit_cost * 1.12) / 100) * 100
    pachka_final = dona_final * pack_size
    real_markup = ((pachka_final / cost) - 1) * 100 if cost > 0 else 0
    return pachka_final, dona_final, real_markup

# PDF-dan jadvalni sug'urib olish funksiyasi
def process_pdf(pdf_file):
    all_rows = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                all_rows.extend(table)
    if all_rows:
        # Birinchi qatorni sarlavha qilib dataframe yaratish
        df_pdf = pd.DataFrame(all_rows[1:], columns=all_rows[0])
        return df_pdf
    return None

# 3. ДИЗАЙН (СИЗНИНГ УЗГАРМАГАН СТИЛИНГИЗ)
def add_custom_style():
    bg_image_url = "https://raw.githubusercontent.com/abbosxolliyev9-tech/MEDEXTRA/main/pexels-eren-34577902.jpg"
    st.markdown(
        f"""
        <style>
        .stApp {{ background-image: url("{bg_image_url}"); background-size: cover; background-position: center; }}
        .blue-label {{ background-color: #004a99; color: white !important; padding: 5px 15px; border-radius: 5px; display: inline-block; font-weight: bold; margin-bottom: 5px; }}
        .stButton>button {{ background-color: #004a99 !important; color: white !important; border-radius: 10px !important; font-weight: bold !important; height: 3em !important; }}
        .footer-box {{ background-color: #004a99; color: white !important; padding: 10px; border-radius: 5px; margin-top: 20px; text-align: center; }}
        .stTextInput label {{ background-color: #004a99 !important; color: white !important; padding: 2px 10px !important; border-radius: 3px !important; }}
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

# ИККИТА АЛОҲИДА БЎЛИМ
tab1, tab2 = st.tabs(["📊 Excel бўлими", "📄 PDF бўлими"])

with tab1:
    uploaded_excel = st.file_uploader("📂 Excel файлларни танланг", type=['xlsx'], accept_multiple_files=True, key="excel_up")
    process_list = uploaded_excel if uploaded_excel else []

with tab2:
    uploaded_pdf = st.file_uploader("📂 PDF фактураларни танланг", type=['pdf'], accept_multiple_files=True, key="pdf_up")
    if uploaded_pdf:
        # PDF-larni vaqtinchalik dataframega aylantirib process_list'ga qo'shamiz
        for pdf_file in uploaded_pdf:
            pdf_df = process_pdf(pdf_file)
            if pdf_df is not None:
                # PDF-ni ham xuddi Excel fayldek ko'rsatish uchun obyekt yaratamiz
                pdf_df.name = pdf_file.name
                process_list.append(pdf_df)

# ҲИСОБЛАШ ҚИСМИ (Ҳар икки турдаги файл учун бир xил ишлайди)
if process_list:
    for i, file_item in enumerate(process_list):
        # Fayl nomini aniqlash (Excel obyekt yoki PDF Dataframe)
        fname = file_item.name if hasattr(file_item, 'name') else f"PDF_Faktura_{i+1}.pdf"
        
        with st.expander(f"📄 {fname}"):
            # Agar bu PDF'dan olingan Dataframe bo'lsa
            if isinstance(file_item, pd.DataFrame):
                df = file_item
            else:
                df = pd.read_excel(file_item)
            
            cols = df.columns.tolist()
            c1, c2 = st.columns(2)
            col_name = c1.selectbox(f"Дори номи устуни", cols, key=f"n_{i}")
            col_cost = c2.selectbox(f"Таннарх устуни", cols, index=min(3, len(cols)-1), key=f"c_{i}")
            
            if st.button(f"🚀 Ҳисоблаш", key=f"b_{i}"):
                p_list, d_list, m_list = [], [], []
                for _, row in df.iterrows():
                    try:
                        val = str(row[col_cost]).replace(' ', '').replace(',', '.')
                        cost = float(re.sub(r'[^\d.]', '', val))
                        size = get_pack_size(row[col_name])
                        p_p, d_p, m_p = calculate_prices(cost, size)
                        p_list.append(p_p); d_list.append(d_p); m_list.append(f"{m_p:.2f}%")
                    except:
                        p_list.append(0); d_list.append(0); m_list.append("0%")
                
                df['Наценка (Фоиз)'] = m_list
                df['Pachka Sotuv'] = p_list
                df['Dona Narxi'] = d_list
                
                st.success("✅ Муваффақиятли ҳисобланди!")
                st.dataframe(df.head(10))
                
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False)
                st.download_button("📥 Натижани Excelда юклаш", output.getvalue(), f"Tayyor_{fname}.xlsx", key=f"d_{i}")
