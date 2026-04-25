import streamlit as st
import pandas as pd
import io
import zipfile
from calculations.logic import get_pack_size, calculate_logic
from tizim.auth import login_system, apply_design, admin_user_management

# 1. DIZAYN VA AUTH TIZIMINI ISHGA TUSHIRISH
apply_design()
login_system()

# Faqat login bo'lgan foydalanuvchilar uchun qolgan qism ishlaydi
if st.session_state.get('logged_in'):
    
    # --- YON MENYU (SIDEBAR) ---
    st.sidebar.title(f"Xush kelibsiz, {st.session_state.user_role}")
    
    # Menyu tanlovlari
    if st.session_state.user_role == "admin":
        menu = ["Admin Hisob-kitob", "Mijoz Hisob-kitob", "Admin Panel (So'rovlar)"]
    else:
        menu = ["Mijoz Hisob-kitob"]
        
    choice = st.sidebar.selectbox("Bo'limni tanlang", menu)

    # --- ADMIN PANEL (SO'ROVLARNI TASDIQLASH) ---
    if choice == "Admin Panel (So'rovlar)":
        admin_user_management()

    # --- HISOB-KITOB BO'LIMLARI ---
    elif choice in ["Admin Hisob-kitob", "Mijoz Hisob-kitob"]:
        st.markdown(f'<div class="main-block">', unsafe_allow_html=True)
        st.subheader(f"📊 {choice} bo'limi")
        
        mode = "admin" if choice == "Admin Hisob-kitob" else "mijoz"
        user_markup = 10
        if mode == "mijoz":
            user_markup = st.select_slider("Ustama foizini tanlang (%):", options=list(range(1, 21)), value=10)

        # Bir nechta faylni yuklash
        uploaded_files = st.file_uploader("Excel fayllarni tanlang", type=['xlsx'], accept_multiple_files=True)

        if uploaded_files:
            processed_files = {} # Hisoblangan fayllarni saqlash uchun
            
            for uploaded_file in uploaded_files:
                st.write(f"📄 Fayl: **{uploaded_file.name}**")
                df = pd.read_excel(uploaded_file)
                cols = df.columns.tolist()
                
                # Ustunlarni aniqlash (Foydalanuvchi tanlaydi)
                c1, c2 = st.columns(2)
                with c1:
                    col_name = st.selectbox(f"Dori nomi ustuni ({uploaded_file.name})", cols, index=0, key=f"n_{uploaded_file.name}")
                with c2:
                    col_cost = st.selectbox(f"Tannarx ustuni ({uploaded_file.name})", cols, index=3 if len(cols)>3 else 0, key=f"c_{uploaded_file.name}")

                # Hisoblash tugmasi
                if st.button(f"Hisoblash: {uploaded_file.name}", key=f"btn_{uploaded_file.name}"):
                    p_res, d_res = [], []
                    
                    for _, row in df.iterrows():
                        try:
                            # Narxni tozalash
                            raw_val = str(row[col_cost]).replace(' ', '').replace(',', '.')
                            import re
                            cost = float(re.sub(r'[^\d.]', '', raw_val))
                        except:
                            cost = 0
                        
                        size = get_pack_size(row[col_name])
                        p_val, d_val = calculate_logic(cost, mode=mode, user_markup=user_markup, pack_size=size)
                        
                        p_res.append(p_val)
                        d_res.append(d_val)
                    
                    df['Pachka Sotuv (H)'] = p_res
                    df['Dona Narxi (I)'] = d_res
                    
                    # Natijani xotirada saqlash
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False)
                    processed_files[uploaded_file.name] = output.getvalue()
                    st.success(f"{uploaded_file.name} muvaffaqiyatli hisoblandi!")

            # ZIP fayl yaratish
            if processed_files:
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                    for name, data in processed_files.items():
                        zip_file.writestr(name, data)
                
                st.markdown("---")
                st.download_button(
                    label="📥 Barcha fayllarni ZIP holatida yuklab olish",
                    data=zip_buffer.getvalue(),
                    file_name="medextra_hisoblar.zip",
                    mime="application/zip"
                )
        st.markdown('</div>', unsafe_allow_html=True)

    # Chiqish tugmasi
    if st.sidebar.button("Log out"):
        st.session_state.logged_in = False
        st.rerun()
