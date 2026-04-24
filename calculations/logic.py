import re
import math

# СОЗЛАМАЛАР
CHEGARA_NARX = 200000
PAST_FOIZ = 1.10  # 10% қўшиш
BALAND_FOIZ = 1.09 # 9% қўшиш

def get_pack_size(name):
    name_upper = str(name).upper()
    if any(word in name_upper for word in ["САЛФЕТКА", "ЧОЙ", "CHAY", "SALFETKA", "МАРЛЯ", "БИНТ"]):
        return 1
    match = re.search(r'[N№](\d+)', name_upper)
    return int(match.group(1)) if match else 1

def admin_calculate(cost, pack_size):
    # Бир дона учун асл таннарх
    unit_cost = cost / (pack_size if pack_size > 0 else 1)
    
    # Таннархга қараб фоизни танлаш (10% ёки 9%)
    pct_rate = BALAND_FOIZ if cost > CHEGARA_NARX else PAST_FOIZ
    
    # Фоиз қўшилган идеал нарх
    target_price = unit_cost * pct_rate
    
    # 100 сўмга юқорига яхлитлаб кўрамиз
    res_unit = math.ceil(target_price / 100) * 100
    
    # Агар яхлитлаш натижасида фоиздан ошиб кетсак, пастга яхлитлаймиз
    if res_unit > target_price:
        res_unit = math.floor(target_price / 100) * 100
    
    # Таннархдан пастга тушиб кетмаслигини таъминлаш
    if res_unit <= unit_cost:
        res_unit = math.ceil(unit_cost / 100) * 100

    pachka_final = res_unit * pack_size
    return int(pachka_final), int(res_unit)

def user_calculate(cost, pack_size, pct):
    pachka_raw = cost * (1 + pct / 100)
    pachka_final = math.ceil(pachka_raw / 100) * 100
    dona_raw = pachka_final / (pack_size if pack_size > 0 else 1)
    dona_final = math.ceil(dona_raw / 100) * 100
    return int(pachka_final), int(dona_final)
