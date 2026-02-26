import streamlit as st
import pandas as pd
import io
import re

st.set_page_config(page_title="MEDEXTRA | Smart Pricing", layout="wide")

def get_pack_size(name):
    """Dori nomidan ichidagi dona sonini aniqlash (masalan N10, №20)"""
    match = re.search(r'[N№](\d+)', str(name))
    return int(match.group(1)) if match else 1

def find_best_price(base_price, pack_size):
    """12% dan 18% gacha optimal foizni qidirish"""
    unit_cost = base_price / pack_size
    best_pct = 12.0
    
    # 12% dan 18% gacha 0.1% qadam bilan tekshiramiz
    for p in range(120, 181):
        current_pct = p / 10.0
        sale_price = unit_cost * (1 + current_pct / 100)
        # Agar narx 100 ga qoldiqsiz bo'linsa (yaxlit bo'lsa)
        if sale_price % 100 == 0:
            return current_pct, sale_price
            
    # Agar chiroyli narx topilmasa, 12% va oddiy 100 gacha yaxlitlash
    final_price = round((unit_cost * 1.12) / 100) * 100
    return 12.0, final_price

# --- Kirish qismi ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("🔐 Kirish")
        user = st.text_input("Login")
        pw = st.text_input("Parol", type="password")
        if st.button("Kirish"):
            if user == "admin" and pw == "12345":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Xato!")
else:
    st.title("💊 MEDEXTRA: Aqlli Inventarizatsiya")
    
    uploaded_file = st.file_uploader("Excel faylni yuklang", type=['xlsx'])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        cols = df.columns.tolist()
        
        # Ustunlarni aniqlash (Rasmga qarab)
        name_col = st.selectbox("Dori nomi ustuni:", cols, index=0)
        price_col = st.selectbox("Sotib olish narxi (Cena):", cols, index=3)
        
        if st.button("🚀 Aqlli hisoblashni boshlash"):
            res_pct = []
            res_unit_price = []
            res_total_price = []
            
            for index, row in df.iterrows():
                name = row[name_col]
                base_price = pd.to_numeric(row[price_col], errors='coerce') or 0
                pack_size = get_pack_size(name)
                
                # Optimal foiz va dona narxini topish
                best_pct, unit_price = find_best_price(base_price, pack_size)
                
                res_pct.append(best_pct)
                res_unit_price.append(unit_price)
                res_total_price.append(unit_price * pack_size)
            
            # G, H, I ustunlariga yozish
            df['Ustama % (G)'] = res_pct
            df['Umumiy sotuv (H)'] = res_total_price
            df['Dona narxi (I)'] = res_unit_price
            
            st.success("Hisoblandi! Tizim 12-18% oralig'ida eng chiroyli narxni tanladi.")
            st.dataframe(df)

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            st.download_button("📥 Faylni yuklab olish", output.getvalue(), "medextra_smart.xlsx")
