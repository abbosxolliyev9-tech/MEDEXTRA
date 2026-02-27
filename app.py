# ... (Олдинги коднинг дизайн ва логин қисми ўзгармайди) ...

if check_password():
    st.markdown("<h1 style='color: white; text-shadow: 2px 2px 10px black; text-align: center;'>📋 Кўп сонли файлларни ҳисоблаш</h1>", unsafe_allow_html=True)

    # 1. Бир нечта файлни юклаш имконияти (accept_multiple_files=True)
    uploaded_files = st.file_uploader("📂 Excel (.xlsx) файлларини танланг", type=['xlsx'], accept_multiple_files=True)

    if uploaded_files:
        st.info(f"Юкланган файллар сони: {len(uploaded_files)}")
        
        # Ҳар бир файл учун алоҳида созламалар ва ҳисоблаш
        for i, file in enumerate(uploaded_files):
            with st.expander(f"📄 Файл: {file.name}", expanded=(i == 0)):
                df = pd.read_excel(file)
                cols = df.columns.tolist()
                
                c1, c2 = st.columns(2)
                with c1:
                    col_name = st.selectbox(f"Дори номи устуни ({i}):", cols, key=f"name_{i}")
                with c2:
                    col_cost = st.selectbox(f"Таннарх устуни ({i}):", cols, index=min(3, len(cols)-1), key=f"cost_{i}")
                
                if st.button(f"🚀 Ҳисоблаш: {file.name}", key=f"btn_{i}"):
                    p_list, d_list = [], []
                    for _, row in df.iterrows():
                        try:
                            val = str(row[col_cost]).replace(' ', '').replace(',', '.')
                            cost = float(re.sub(r'[^\d.]', '', val))
                        except: cost = 0
                        
                        size = get_pack_size(row[col_name])
                        p_p, d_p = calculate_prices(cost, size)
                        p_list.append(p_p)
                        d_list.append(d_p)
                    
                    df['Pachka Sotuv (H)'] = p_list
                    df['Dona Narxi (I)'] = d_list
                    
                    st.success(f"✅ {file.name} ҳисобланди!")
                    st.dataframe(df.head(10)) # Намуна сифатида 10 та қатор
                    
                    # Юклаб олиш тугмаси
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False)
                    st.download_button(
                        label=f"📥 {file.name} натижасини юклаш",
                        data=output.getvalue(),
                        file_name=f"resolved_{file.name}",
                        key=f"dl_{i}",
                        use_container_width=True
                    )
