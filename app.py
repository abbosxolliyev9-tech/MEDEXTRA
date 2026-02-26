import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="MEDEXTRA | Excel Pro", layout="wide")

# Parol tizimi
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
    st.title("💊 MEDEXTRA: Excel Avtomatizatsiya")
    
    with st.sidebar:
        st.header("⚙️ Hisob qoidalari")
        pct = st.number_input("Ustama foizi (%)", min_value=0, max_value=100, value=15)
        st.write("G ustun: Foiz")
        st.write("H ustun: Umumiy summa")
        st.write("I ustun: Donasi (Narxi)")

    uploaded_file = st.file_uploader("Excel faylni yuklang", type=['xlsx'])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        
        # Ustunlar borligini tekshirish (D ustuni 'Cena' ekan rasmda)
        # Ekranda 4-ustun (D) narx ekanini ko'ryapman
        try:
            # 1. G katak: Necha foiz qo'yilgani
            df['Ustama %'] = pct
            
            # 2. H katak: Foiz qo'yilgandagi umumiy narxi (Narx * miqdor * foiz)
            # Rasmda: D ustuni (Cena), C ustuni (Kolichestvo)
            df['Umumiy Sotuv summasi'] = (df.iloc[:, 3] * df.iloc[:, 2] * (1 + pct/100)).apply(lambda x: round(x / 100) * 100)
            
            # 3. I katak: Dorining donasini sotuv narxi
            df['Dona sotuv narxi'] = (df.iloc[:, 3] * (1 + pct/100)).apply(lambda x: round(x / 100) * 100)
            
            st.success("Hisoblandi! G, H va I ustunlari shakllantirildi.")
            st.dataframe(df)

            # Faylni yuklab olish uchun tayyorlash
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Hisobot')
            
            st.download_button(
                label="📥 Tayyor Excelni yuklab olish",
                data=output.getvalue(),
                file_name="medextra_tayyor.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Xatolik: Excel formati mos kelmadi. Ustunlarni tekshiring! {e}")
