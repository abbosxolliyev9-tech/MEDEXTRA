import re
import math

def get_pack_size(name):
    """Dori nomidan № sonini qidiradi"""
    name_str = str(name).upper()
    match = re.search(r'[N№](\d+)', name_str)
    return int(match.group(1)) if match else 1

def calculate_logic(cost, mode="admin", user_markup=10, pack_size=1):
    """Asosiy hisob-kitob mantiqi"""
    if cost <= 0: return 0, 0
    
    # 1. Ustama foizini aniqlash
    if mode == "admin":
        markup = 1.08 if cost >= 300000 else 1.10
        round_val = 50 # Admin uchun 50 so'mga yaxlitlash
    else:
        markup = 1 + (user_markup / 100)
        round_val = 100 # Mijoz uchun 100 so'mga yaxlitlash
    
    # 2. Pachka narxi
    pachka_raw = cost * markup
    pachka_final = math.ceil(pachka_raw / round_val) * round_val
    
    # 3. Dona narxi
    dona_raw = pachka_final / pack_size
    dona_final = math.ceil(dona_raw / 100) * 100
    
    return int(pachka_final), int(dona_final)
