import math
import re

def get_pack_size(name):
    name_str = str(name).upper()
    match = re.search(r'[N№](\d+)', name_str)
    return int(match.group(1)) if match else 1

def calculate_logic(cost, mode, markup_val=10):
    if cost <= 0: return 0, 0
    
    # 1. Admin: >300k бўлса 8%, <300k бўлса 10%
    if mode == "Админ Ҳисоб":
        markup = 1.08 if cost >= 300000 else 1.10
    # 2. Mijoz: Фоизни ўзи белгилайди
    else:
        markup = 1 + (markup_val / 100)
        
    pachka_raw = cost * markup
    # 100 сўмга яхлитлаш
    pachka_final = math.ceil(pachka_raw / 100) * 100
    return int(pachka_final)
