import streamlit as st
import pandas as pd
import io
import re

st.set_page_config(page_title="MEDEXTRA | Smart Pricing", layout="wide")

def get_pack_size(name):
    """Dori nomidan dona sonini aniqlash (N10, №20 va h.k.)"""
    name_str = str(name).upper()
    match = re.search(r'[N№](\d+)', name_str)
    if match:
        size = int(match.group(1))
        return size if size > 0 else 1
    return 1

def find_smart_price(base_price, pack_size):
    """12% dan 18% gacha optimal yaxlit narxni topish"""
    if pack_size <= 0: pack_size = 1
    unit_cost = base_price / pack_size
    
    # 12.0% dan 18.0% gacha 0.1% qadam bilan qidiramiz
    for p in range(120, 181):
        pct = p / 10.0
        sale_price = unit_cost * (1 + pct / 100)
        # Agar narx 100 ga roppa-rosa bo'linsa (masalan 1200, 1500)
        if round(sale_price, 2) % 100 == 0:
            return pct, round(sale_price)
            
    # Agar chiroyli narx topilmasa, 12% qo'shib, oddiy 100 gacha yaxlitlaymiz
    final_price = round((unit_cost * 1.12) / 100) * 100
    if final_price == 0: final_price = round(unit_cost) # Juda arzon dori bo'lsa
    return 12.0, final_price

# --- Login qismi ---
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
    st.title("💊 MEDEXTRA: Aqlli Narx Tizimi")
    
    uploaded_file = st.file_uploader("Faqat Excel (.xlsx) yuklang", type=['xlsx'])

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            cols = df.columns.tolist()
            
            st.info("Jadval o'qildi. Ustunlarni tekshiring:")
            col_a = st.selectbox("Dori nomi ustuni (A):", cols, index=0)
            col_d = st.selectbox("Sotib olish narxi (D):", cols, index=3 if len(cols)>3 else 0)
            
            if st.button("🚀 Aqlli hisoblashni boshlash"):
                p_list, h_list, i_list = [], [], []
                
                for _, row in df.iterrows():
                    name = row[col_a]
                    # Narxdagi bo'shliq yoki harflarni tozalash
                    raw_price = str(row[col_d]).replace(' ', '').replace(',', '.')
                    try:
                        base_price = float(re.sub(r'[^\d.]', '', raw_price))
                    except:
                        base_price = 0
                    
                    pack_size = get_pack_size(name)
                    
                    # Hisoblash
                    best_pct, unit_price = find_smart_price(base_price, pack_size)
                    
                    p_list.append(best_pct)
                    i_list.append(unit_price)
                    h_list.append(unit_price * pack_size)
                
                # Yangi ustunlarni qo'shish
                df['Ustama % (G)'] = p_list
                df['Umumiy sotuv (H)'] = h_list
                df['Dona narxi (I)'] = i_list
                
                st.success("Bajarildi! Dona narxi (I) 100 so'mga yaxlitlandi.")
                st.dataframe(df)

                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False)
                st.download_button("📥 Faylni yuklab olish", output.getvalue(), "medextra_yakuniy.xlsx")
                
        except Exception as e:
            st.error(f"Kutilmagan xato: {e}")
