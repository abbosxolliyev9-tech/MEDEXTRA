import re
import math

def get_pack_size(name):
    name_str = str(name).upper()
    match = re.search(r'[N№](\d+)', name_str)
    return int(match.group(1)) if match else 1

def calculate_logic(cost, mode="admin", user_markup=10, pack_size=1):
    if cost <= 0:
        return 0, 0

    if mode == "admin":
        # Admin qoidasi: 300 000 dan tepa 8%, past 10%
        markup = 1.08 if cost >= 300000 else 1.10
        pachka_raw = cost * markup
        # Admin uchun 50 so'mga yaxlitlash (siz yozgan qoida bo'yicha)
        pachka_final = math.ceil(pachka_raw / 50) * 50
    else:
        # Mijoz rejimi
        markup = 1 + (user_markup / 100)
        pachka_raw = cost * markup
        pachka_final = math.ceil(pachka_raw / 100) * 100

    dona_raw = pachka_final / pack_size
    dona_final = math.ceil(dona_raw / 100) * 100

    return int(pachka_final), int(dona_final)
