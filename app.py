import streamlit as st
import pandas as pd
import io
import re
import math

st.set_page_config(page_title="MEDEXTRA", layout="wide")
st.title("💊 MEDEXTRA: To'g'ri Narxlash")

def find_smart_price(total_cost):
    """Tannarxga 12% qo'shib, faqat tepaga 100 ga yaxlitlaydi"""
    if total_cost <= 0: return 12.0, 0
    
    # Tannarxga 12% qo'shish
    sale_price = total_cost * 1.12
    
    # Natijani faqat tepaga 100 ga yaxlitlash (Masalan: 7116 -> 7200)
    final_price = math.ceil(sale_price / 100) * 100
    
    return 12.0, int(final_price)

uploaded_file = st.file_uploader("Excel (.xlsx) yuklang", type=['xlsx'])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    cols = df.columns.tolist()
    
    col_a = st.selectbox("Dori nomi (A):", cols, index=0)
    col_d = st.selectbox("Tannarx (D):", cols, index=3 if len(cols)>3 else 0)
    
    if st.button("🚀 Hisoblash"):
        p_list, h_list = [], []
        
        for _, row in df.iterrows():
            try:
                # Tannarxni tozalash
                raw_p = str(row[col_d]).replace(' ', '').replace(',', '.')
                price = float(re.sub(r'[^\d.]', '', raw_p))
            except:
                price = 0
            
            # Faqat bitta oddiy qoida: Tannarx + 12% va yaxlitlash
            pct, final_p = find_smart_price(price)
            
            p_list.append(pct)
            h_list.append(final_p)
        
        df['Ustama % (G)'] = p_list
        df['Sotuv Narxi (H)'] = h_list
        
        st.success("Hisoblandi! Endi narxlar aniq 12% ustama bilan (tepaga yaxlitlangan).")
        st.dataframe(df)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        st.download_button("📥 Yuklab olish", output.getvalue(), "medextra_final.xlsx")
