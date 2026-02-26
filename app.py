import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="MEDEXTRA | Professional", layout="wide")

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
    st.title("💊 MEDEXTRA: Narx Hisoblagich")
    
    with st.sidebar:
        st.header("⚙️ Sozlamalar")
        pct = st.number_input("Ustama foizi (%)", 0, 100, 15)

    uploaded_file = st.file_uploader("Excel faylni yuklang", type=['xlsx'])

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            st.info("Jadval o'qildi. Narx ustunini tanlang.")
            
            cols = df.columns.tolist()
            price_col = st.selectbox("Sotib olingan narx ustuni (Cena):", cols)
            qty_col = st.selectbox("Miqdor ustuni (Kolichestvo):", cols)

            if st.button("🚀 Hisoblashni boshlash"):
                # Narxlarni songa aylantirish (xatolik bermasligi uchun)
                df[price_col] = pd.to_numeric(df[price_col], errors='coerce').fillna(0)
                df[qty_col] = pd.to_numeric(df[qty_col], errors='coerce').fillna(0)

                # G: Foiz
                df['Ustama %'] = pct
                
                # I: Donasining sotuv narxi (yaxlitlangan)
                df['Dona sotuv narxi (I)'] = (df[price_col] * (1 + pct/100)).apply(lambda x: round(x / 100) * 100)
                
                # H: Umumiy sotuv summasi (Narx * Miqdor * Foiz)
                df['Umumiy sotuv summasi (H)'] = (df[price_col] * df[qty_col] * (1 + pct/100)).apply(lambda x: round(x / 100) * 100)

                st.success("Muvaffaqiyatli hisoblandi!")
                st.dataframe(df)

                # Export
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False)
                
                st.download_button("📥 Tayyor Excelni yuklab olish", output.getvalue(), "medextra_hisob.xlsx")
        
        except Exception as e:
            st.error(f"Faylni o'qishda xato: {e}")
