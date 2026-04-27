import re
import math

def get_pack_size(name):
    match = re.search(r'[N№](\d+)', str(name).upper())
    return int(match.group(1)) if match else 1

def calculate_logic(cost, mode="admin", user_markup=10, pack_size=1):
    if cost <= 0: return 0, 0
    if mode == "admin":
        markup = 1.08 if cost >= 300000 else 1.10
    else:
        markup = 1 + (user_markup / 100)
    
    pachka_raw = cost * markup
    pachka_final = math.ceil(pachka_raw / 100) * 100
    dona_final = math.ceil((pachka_final / pack_size) / 100) * 100
    return int(pachka_final), int(dona_final)
