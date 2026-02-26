import streamlit as st
import pandas as pd
import io
import re
import math

st.set_page_config(page_title="MEDEXTRA | Universal", layout="wide")
st.title("💊 MEDEXTRA: Aqlli Narx Tizimi")

def get_pack_size(name):
    """Dori nomidan N10, N20 kabi dona sonini topish"""
    name_str = str(name).upper()
    match = re.search(r'[N№](\d+)', name_str)
    return int(match.group(1)) if match else 1

def find_smart_price(base_price, pack_size):
    """Barcha dorilar uchun 12-18% oraliqda optimal narx topish"""
    unit_cost = base_price / (pack_size if pack_size > 0 else 1)
    
    # 1. 12% dan 18% gacha 0.1% qadam bilan 'chiroyli' narx qidirish
    for p in range(120, 181):
        pct = p / 10.0
        sale_price = unit_cost * (1 + pct / 100)
        # Agar narx 100 ga qoldiqsiz bo'linsa (masalan 7200, 8500)
        if round(sale_price, 2) % 100 == 0:
            return pct, int(sale_price)
            
    # 2. Agar chiroyli narx topilmasa, 12% qo'shib faqat TEPAGA yaxlitlash
    min_sale = unit_cost * 1.12
    final_price = math.ceil(min_sale / 100) * 100
    return 12.0, int(final_price)

uploaded_file = st.file_uploader("Excel (.xlsx) faylni yuklang", type=['xlsx'])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        cols = df.columns.tolist()
        
        # Ustunlarni avtomatik yoki qo'lda tanlash
        col_a = st.selectbox("Dori nomi ustuni (A):", cols, index=0)
        col_d = st.selectbox("Tannarx ustuni (D):", cols, index=3 if len(cols)>3 else 0)
        
        if st.button("🚀 Barcha dorilarni hisoblash"):
            p_list, h_list, i_list = [], [], []
            
            for index, row in df.iterrows():
                # Narxdagi probel va belgilarni tozalash
                raw_p = str(row[col_d]).replace(' ', '').replace(',', '.')
                try:
                    price = float(re.sub(r'[^\d.]', '', raw_p))
                except:
                    price = 0
                
                size = get_pack_size(row[col_a])
                pct, unit_p = find_smart_price(price, size)
                
                p_list.append(pct)
                i_list.append(unit_p)
                h_list.append(unit_p * size)
            
            df['Ustama % (G)'] = p_list
            df['Jami Sotuv (H)'] = h_list
            df['Dona Narxi (I)'] = i_list
            
            st.success("Barcha dorilar 12-18% oralig'ida muvaffaqiyatli hisoblandi!")
            st.dataframe(df)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            st.download_button("📥 Natijani yuklab olish", output.getvalue(), "medextra_hisobot.xlsx")
            
    except Exception as e:
        st.error(f"Xato: {e}")
