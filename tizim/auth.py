import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 1. DIZAYN SOZLAMALARI (RASM VA KONTAKT)
BACKGROUND_IMAGE = "pexels-eren-34577902.jpg"  # Shu yerda rasmni osongina almashtirishingiz mumkin
CONTACT_PHONE = "+998887549896"

def apply_design():
    """Sayt orqa foni va pastki qismidagi kontaktni sozlash"""
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("{BACKGROUND_IMAGE}");
            background-size: cover;
            background-attachment: fixed;
        }}
        .auth-container {{
            background: rgba(0, 0, 0, 0.8);
            padding: 30px;
            border-radius: 15px;
            color: white;
            border: 1px solid #27AE60;
            margin-top: 50px;
        }}
        .footer {{
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: rgba(0, 0, 0, 0.7);
            color: white;
            text-align: center;
            padding: 10px;
            font-size: 16px;
        }}
        </style>
        <div class="footer">Bog'lanish uchun: {CONTACT_PHONE}</div>
    """, unsafe_allow_html=True)

# 2. GOOGLE SHEETS BILAN BOG'LANISH
def connect_gsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
    client = gspread.authorize(creds)
    # Google Sheets-da 'Users' nomli varaq bo'lishi shart
    sheet = client.open("MEDEXTRA_DB").worksheet("Users")
    return sheet

# 3. LOGIN VA REGISTRATSIYA TIZIMI
def login_system():
    apply_design()
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_role = None

    if not st.session_state.logged_in:
        tab1, tab2 = st.tabs(["🔐 Kirish", "📝 Registratsiya"])

        with tab1:
            st.markdown('<div class="auth-container">', unsafe_allow_html=True)
            user = st.text_input("Login")
            pw = st.text_input("Parol", type="password")
            
            if st.button("Kirish"):
                # Admin tekshiruvi
                if user == "admin" and pw == "Abbos96":
                    st.session_state.logged_in = True
                    st.session_state.user_role = "admin"
                    st.rerun()
                else:
                    # Mijozlarni Google Sheets-dan tekshirish
                    try:
                        sheet = connect_gsheet()
                        data = sheet.get_all_records()
                        for row in data:
                            if str(row['login']) == user and str(row['parol']) == pw:
                                if row['status'] == 1:
                                    st.session_state.logged_in = True
                                    st.session_state.user_role = "mijoz"
                                    st.rerun()
                                else:
                                    st.error("Sizning so'rovingiz hali tasdiqlanmagan!")
                                    return
                        st.error("Login yoki parol noto'g'ri!")
                    except Exception as e:
                        st.error("Tizimga ulanishda xato!")
            st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown('<div class="auth-container">', unsafe_allow_html=True)
            st.subheader("Registratsiya uchun so'rov qoldiring")
            new_name = st.text_input("Ismingiz")
            new_phone = st.text_input("Telefon raqamingiz (masalan: 998887549896)")
            
            if st.button("So'rov yuborish"):
                if new_name and new_phone:
                    try:
                        sheet = connect_gsheet()
                        # Yangi so'rovni status=0 (kutilmoqda) bilan qo'shish
                        sheet.append_row([new_name, new_phone, 0]) 
                        st.success("So'rovingiz yuborildi! Admin tasdiqlashini kuting.")
                    except:
                        st.error("Xatolik yuz berdi!")
                else:
                    st.warning("Ma'lumotlarni to'liq kiriting!")
            st.markdown('</div>', unsafe_allow_html=True)

# 4. ADMIN PANEL: Mijozlarni tasdiqlash funksiyasi
def admin_user_management():
    st.subheader("👥 Mijozlar so'rovlarini boshqarish")
    try:
        sheet = connect_gsheet()
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        
        waiting_users = df[df['status'] == 0]
        
        if not waiting_users.empty:
            for i, row in waiting_users.iterrows():
                col1, col2 = st.columns([3, 1])
                col1.write(f"Ism: {row['login']} | Tel: {row['parol']}")
                if col2.button("Tasdiqlash", key=f"btn_{i}"):
                    # G-sheetda statusni 1 ga o'zgartirish (2-qatordan boshlanadi + i)
                    cell = sheet.find(str(row['parol']))
                    sheet.update_cell(cell.row, 3, 1)
                    st.success(f"{row['login']} tasdiqlandi!")
                    st.rerun()
        else:
            st.write("Yangi so'rovlar yo'q.")
    except:
        st.write("Ma'lumotlar bazasiga ulanib bo'lmadi.")
