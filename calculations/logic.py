import re
import math

def get_pack_size(name):
    """
    Dori nomidan №8, №10 yoki N30 kabi sonni qidirib topadi.
    Agar topilmasa, dori 1 dona deb hisoblanadi.
    """
    name_str = str(name).upper()
    # № yoki N dan keyin kelgan raqamlarni ushlab oladi
    match = re.search(r'[N№](\d+)', name_str)
    if match:
        return int(match.group(1))
    return 1

def calculate_logic(cost, mode="admin", user_markup=10, pack_size=1):
    """
    Asosiy hisob-kitob mantiqi.
    cost: Tannarx
    mode: "admin" yoki "mijoz"
    user_markup: Mijoz tanlagan foiz (1-20)
    pack_size: № soni
    """
    if cost <= 0:
        return 0, 0

    # 1. Ustama foizini aniqlash
    if mode == "admin":
        # Admin qoidasi: 300 000 dan tepa 8%, past 10%
        markup = 1.08 if cost >= 300000 else 1.10
    else:
        # Mijoz rejimi: foydalanuvchi tanlagan foiz
        markup = 1 + (user_markup / 100)

    # 2. Pachka narxini hisoblash va 100 so'mga tepaga yaxlitlash
    pachka_raw = cost * markup
    pachka_final = math.ceil(pachka_raw / 100) * 100

    # 3. Dona narxini hisoblash va 100 so'mga tepaga yaxlitlash
    dona_raw = pachka_final / pack_size
    dona_final = math.ceil(dona_raw / 100) * 100

    return int(pachka_final), int(dona_final)
