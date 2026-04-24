import streamlit as st
import pandas as pd
import io
import re
import math
import hashlib
import zipfile

# 1. SAHIFA SOZLAMALARI
st.set_page_config(page_title="MEDEXTRA", page_icon="💊", layout="centered")

# 2. DIZAYN
def add_custom_style():
    bg_image = "https://raw.githubusercontent.com/abbosxolliyev9-tech/MEDEXTRA/main/pexels-eren-34577902.jpg"
    st.markdown(f"""
        <style>
        .stApp {{ background-image: url("{bg_image}"); background-size: cover; background-position: center; }}
        .blue-label {{ background-color: #004a99; color: white !important; padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 20px; margin-bottom: 20px; border: 1px solid white; }}
        .contact-box {{ background-color: rgba(0, 74, 153, 0.85); color: white; padding: 12px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 16px; margin-top: 25px; border: 2px solid white; }}
        .stButton>button {{ background-color: #004a99 !important; color: white !important; width: 100%; font-weight: bold; border-radius: 8px; height: 45px; border: 1px solid white; }}
        [data-testid="stSidebar"] {{ background-color: rgba(0, 74, 153, 0.95); }}
        [data-testid="stSidebar"] * {{ color: white !important; }}
        </style>
        """, unsafe_allow_html=True)

add_custom_style()

# 3. GOOGLE SHEETS ULANISHI
SHEET_URL = "https://docs.google.com/spreadsheets/d/1XyO5EqqDonEfQnmqr8j7SQNbVcx2SC93txhFVHoDGQA/export?format=csv"

def load_users_data():
    try: return pd.read_csv(SHEET_URL)
    except: return pd.DataFrame(columns=['phone', 'password', 'name', 'status'])

# 4. МАТЕМАТИК ФУНКЦИЯЛАР (ЯНГИ ВА ХАВФСИЗ ВАРИАНТ)
def get_pack_size(name):
    name_upper = str(name).upper()
    if any(word in name_upper for word in ["САЛФЕТКА", "ЧОЙ", "CHAY", "SALFETKA", "МАРЛЯ", "БИНТ"]): return 1
    match = re.search(r'[N№](\d+)', name_upper)
    return int(match.group(1)) if match else 1

def admin_calculate(cost, pack_size):
    # 1. Бир дона учун таннархни ҳисоблаймиз
    unit_cost = cost / (pack_size if pack_size > 0 else 1)
    
    # 2. Фоизни танлаймиз: 200к дан паст бўлса 10%, баланд бўлса 9%
    pct_rate = 1.10 if cost <= 200000 else 1.09
    
    # 3. Максимал рухсат этилган чегара (фоиздан ошиб кетмаслиги учун)
    max_allowed = unit_cost * pct_rate
    
    # 4. 100 сўмга юқорига яхлитлаб кўрамиз
    res_unit = math.ceil((unit_cost * pct_rate) / 100) * 100
    
    # 5. Агар яхлитлаш натижасида фоиз чегарасидан ошиб кетсак, пастга яхлитлаймиз
    if res_unit > max_allowed:
        res_unit = math.floor(max_allowed / 100) * 100
    
    # 6. Агар пастга яхлитлаш таннархдан ҳам пастга тушириб юборса, таннархни юқорига 100 га яхлитлаймиз
    if res_unit <= unit_cost:
        res_unit = math.ceil(unit_cost / 100) * 100

    pachka_final = res_unit * pack_size
    return int(pachka_final), int(res_unit)

def user_calculate(cost, pack_size, pct):
    # Фоизли калькулятор учун ҳам 100 сўмлик яхлитлаш
    pachka_raw = cost * (1 + pct / 100)
    pachka_final = math.ceil(pachka_raw / 100) * 100
    
    dona_raw = pachka_final / (pack_size if pack_size > 0 else 1)
    dona_final = math.ceil(dona_raw / 100) * 100
    
    return int(pachka_final), int(dona_final)

# 5. LOGIN TIZIMI
if "auth" not in st.session_state: st.session_state["auth"] = False

if not st.session_state["auth"]:
    tab_log, _ = st.tabs(["🔑 КИРИШ", "📝 РЎЙХАТДАН ЎТИШ"])
    with tab_log:
        st.markdown('<div class="blue-label">Тизимга кириш</div>', unsafe_allow_html=True)
        login_u = st.text_input("Логин / Телефон")
        login_p = st.text_input("Парол", type="password")
        if st.button("КИРИШ"):
            users_df = load_users_data()
            entered_hash = hashlib.sha256(login_p.encode()).hexdigest()
            user_row = users_df[users_df['phone'].astype(str) == str(login_u)]
            if not user_row.empty:
                db_pass = str(user_row.iloc[0]['password'])
                if (db_pass == entered_hash or db_pass == login_p) and int(user_row.iloc[0]['status']) > 0:
                    st.session_state["auth"] = True
                    st.session_state["role"] = int(user_row.iloc[0]['status'])
                    st.rerun()
                else: st.error("Парол хато ёки статус актив эмас!")
            else: st.error("Фойдаланувчи топилмади!")
    st.markdown('<div class="contact-box">📞 Боғланиш: +998 88 754 98 96</div>', unsafe_allow_html=True)
    st.stop()

# 6. MENU (SIDEBAR)
st.sidebar.title("💎 MEDEXTRA")
menu = st.sidebar.radio("Бўлим:", ["🚀 Админ Ҳисоб", "📊 Фоизли Кальк", "⚙️ Панел"] if st.session_state.get("role") == 9 else ["📊 Фоизли Кальк"])

# 7. ИШЧИ ҚИСМЛАР
if menu in ["🚀 Админ Ҳисоб", "📊 Фоизли Кальк"]:
    title = "АДМИН ҲИСОБЛАШ (14-12-10%)" if menu == "🚀 Админ Ҳисоб" else "ИХТИЁРИЙ ФОИЗЛИ ҲИСОБЛАШ"
    st.markdown(f'<div class="blue-label">{title}</div>', unsafe_allow_html=True)
    
    if menu == "📊 Фоизли Кальк":
        user_pct = st.slider("Устама фоизини танланг:", 1, 25, 12)
    
    # Кўп файл юклаш имконияти
    uploaded_files = st.file_uploader("Excel файлларни юкланг", type=['xlsx'], accept_multiple_files=True)
    
    if uploaded_files:
        # Биринчи файлдан устунларни аниқлаб оламиз
        sample_df = pd.read_excel(uploaded_files[0])
        cols = sample_df.columns.tolist()
        
        c1, c2 = st.columns(2)
        col_n = c1.selectbox("💊 Номи устуни (A):", cols, index=0)
        col_c = c2.selectbox("💰 Таннарх устуни (E):", cols, index=min(4, len(cols)-1))
        
        if st.button("🚀 ҲАММАСИНИ ҲИСОБЛАШ ВА ZIP ҚИЛИШ"):
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for f in uploaded_files:
                    try:
                        df = pd.read_excel(f)
                        p_l, d_l = [], []
                        for _, row in df.iterrows():
                            try:
                                cost = float(re.sub(r'[^\d.]', '', str(row[col_c]).replace(',','.')))
                                pack = get_pack_size(row[col_n])
                                if menu == "🚀 Админ Ҳисоб": p_f, d_f = admin_calculate(cost, pack)
                                else: p_f, d_f = user_calculate(cost, pack, user_pct)
                                p_l.append(p_f); d_l.append(d_f)
                            except: p_l.append(0); d_l.append(0)
                        
                        df['Sotuv_Pachka'], df['Sotuv_Dona'] = p_l, d_l
                        
                        # Файлни хотирада сақлаш
                        excel_out = io.BytesIO()
                        with pd.ExcelWriter(excel_out, engine='xlsxwriter') as wr:
                            df.to_excel(wr, index=False)
                        
                        # ZIP ичига қўшиш
                        zf.writestr(f"Tayyor_{f.name}", excel_out.getvalue())
                    except Exception as e:
                        st.error(f"Хатолик: {f.name} - {e}")
            
            st.success(f"✅ {len(uploaded_files)} та файл муваффақиятли ҳисобланди!")
            st.download_button(
                label="📥 ZIP АРХИВНИ ЮКЛАБ ОЛИШ",
                data=zip_buffer.getvalue(),
                file_name="MedExtra_Natijalar.zip",
                mime="application/zip"
            )

elif menu == "⚙️ Панел":
    st.markdown('<div class="blue-label">⚙️ БОШҚАРУВ</div>', unsafe_allow_html=True)
    st.link_button("🌐 Google Sheets-ни очиш", SHEET_URL.replace('/export?format=csv', '/edit'))

st.markdown('<div class="contact-box">📞 Боғланиш учун: +998 88 754 98 96</div>', unsafe_allow_html=True)
