import streamlit as st
import pandas as pd
import io
import zipfile
import re
import math

# 1. САҲИФА СОЗЛАМАЛАРИ
st.set_page_config(page_title="MEDEXTRA ULTIMATE", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .main-block { background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 15px; border: 1px solid #27AE60; }
    </style>
    """, unsafe_allow_html=True)

# 2. МУКАММАЛ НАРХЛАШ ФУНКЦИЯСИ
def get_pack_size(name):
    match = re.search(r'[N№](\d+)', str(name).upper())
    return int(match.group(1)) if match else 1

def smart_price_engine(cost):
    if cost <= 0: return 0
    
    # Яхлитлаш қадамлари устуворлиги
    rounding_steps = [1000, 500, 100, 50, 10]
    
    # 1-БОСҚИЧ: 10.99% дан 8.00% гача пастга қараб қидириш
    # Аввал 1000 сўмликни барча фоизларда текширамиз, кейин 500 сўмликни ва ҳ.к.
    for step in rounding_steps:
        # Фоизни 10.99 дан 8.00 гача 0.01 қадам билан текшириш
        # range ишлатиб бўлмайди, шунинг учун while ишлатамиз
        current_pct = 10.99
        while current_pct >= 8.00:
            target_multiplier = 1 + (current_pct / 100)
            # Нархни шу фоизда ҳисоблаб, шу 'step' га яхлитлаб кўрамиз
            # Пастга яхлитлаймиз (чунки сиз пастга қараб қидириш дедингиз)
            candidate = (cost * target_multiplier // step) * step
            
            # Энди шу номзод нархнинг реал фоиз ставкасини текширамиз
            real_markup = (candidate / cost) - 1
            
            # Агар бу нарх 8% ва 10.99% оралиғига тушса - БУ ҒАЛАБА!
            if 0.08 <= real_markup <= 0.10999:
                return int(candidate)
            
            current_pct -= 0.01 # Фоизни 0.01 га камайтириб борамиз
            
    # 2-БОСҚИЧ: Агар юқоридаги оралиқда ҳеч қандай яхлит нарх топилмаса
    # Унда 11% дан 19% гача тепага қараб қидирамиз
    for pct in range(11, 20):
        target_multiplier = 1 + (pct / 100)
        for step in rounding_steps:
            candidate = math.ceil((cost * target_multiplier) / step) * step
            if candidate > cost:
                return int(candidate)
                
    return int(math.ceil(cost * 1.10 / 10) * 10)

# 3. INTERFACE
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown('<div class="main-block">', unsafe_allow_html=True)
    st.title("💊 MEDEXTRA ULTIMATE")
    u, p = st.text_input("Login"), st.text_input("Parol", type="password")
    if st.button("Кириш"):
        if (u == "admin" and p == "Abbos96") or (u == "mijoz" and p == "123"):
            st.session_state.auth = True
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.header("📊 Профессионал Нархлаш Фильтри")
    uploaded_files = st.file_uploader("Excel файлларни юкланг", accept_multiple_files=True)
    
    if uploaded_files:
        configs = {}
        for f in uploaded_files:
            df_preview = pd.read_excel(f, nrows=0)
            cols = df_preview.columns.tolist()
            st.write(f"📄 {f.name}")
            c1, c2 = st.columns(2)
            configs[f.name] = {
                "n": c1.selectbox("Номи", cols, key=f"n_{f.name}"),
                "c": c2.selectbox("Таннархи", cols, index=min(3, len(cols)-1), key=f"c_{f.name}")
            }

        if st.button("🚀 ҲИСОБЛАШНИ БОШЛАШ"):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for f in uploaded_files:
                    df = pd.read_excel(f)
                    cfg = configs[f.name]
                    p_res, d_res = [], []
                    
                    for _, row in df.iterrows():
                        try:
                            val = str(row[cfg['c']]).replace(' ','').replace(',','.')
                            cost = float(re.sub(r'[^\d.]', '', val))
                        except: cost = 0
                        
                        # Пачка нархи
                        p_price = smart_price_engine(cost)
                        # Дона нархи
                        size = get_pack_size(row[cfg['n']])
                        d_price = smart_price_engine(p_price / size) if size > 1 else p_price
                        
                        p_res.append(p_price)
                        d_res.append(d_price)
                    
                    df['Sotuv_Pachka'] = p_res
                    df['Sotuv_Dona'] = d_res
                    
                    output = io.BytesIO()
                    df.to_excel(output, index=False)
                    zf.writestr(f"Tayyor_{f.name}", output.getvalue())
            
            st.success("Ҳисоблаш якунланди!")
            st.download_button("📥 ZIP архивни юклаб олиш", zip_buffer.getvalue(), "medextra_ultimate.zip")
