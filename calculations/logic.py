import re
import math

# СОЗЛАМАЛАР
CHEGARA_NARX = 200000
PAST_FOIZ = 1.10  
BALAND_FOIZ = 1.09 

def get_pack_size(name):
    name_upper = str(name).upper()
    if any(word in name_upper for word in ["САЛФЕТКА", "ЧОЙ", "CHAY", "SALFETKA", "МАРЛЯ", "БИНТ"]):
        return 1
    match = re.search(r'[N№](\d+)', name_upper)
    return int(match.group(1)) if match else 1

def admin_calculate(cost, pack_size):
    unit_cost = cost / (pack_size if pack_size > 0 else 1)
    pct = BALAND_FOIZ if cost > CHEGARA_NARX else PAST_FOIZ
    limit_price = unit_cost * pct
    res_unit = math.ceil(limit_price / 100) * 100
    if res_unit > limit_price:
        res_unit = math.floor(limit_price / 100) * 100
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
