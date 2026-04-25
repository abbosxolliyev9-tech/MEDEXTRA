import re
import math
import pandas as pd
import io
import zipfile

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
    return int(res_unit * pack_size), int(res_unit)

def user_calculate(cost, pack_size, pct):
    pachka_raw = cost * (1 + pct / 100)
    pachka_final = math.ceil(pachka_raw / 100) * 100
    dona_raw = pachka_final / (pack_size if pack_size > 0 else 1)
    dona_final = math.ceil(dona_raw / 100) * 100
    return int(pachka_final), int(dona_final)

# ЯНГИ: Файлларни қайта ишлаш функцияси
def process_excel_files(uploaded_files, menu_type, col_n, col_c, user_pct=None):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        for f in uploaded_files:
            df = pd.read_excel(f)
            p_l, d_l = [], []
            for _, row in df.iterrows():
                try:
                    cost = float(re.sub(r'[^\d.]', '', str(row[col_c]).replace(',','.')))
                    pack = get_pack_size(row[col_n])
                    if menu_type == "🚀 Админ Ҳисоб":
                        p_f, d_f = admin_calculate(cost, pack)
                    else:
                        p_f, d_f = user_calculate(cost, pack, user_pct)
                    p_l.append(p_f); d_l.append(d_f)
                except:
                    p_l.append(0); d_l.append(0)
            
            df['Sotuv_Pachka'] = p_l
            df['Sotuv_Dona'] = d_l
            
            excel_out = io.BytesIO()
            with pd.ExcelWriter(excel_out, engine='xlsxwriter') as wr:
                df.to_excel(wr, index=False)
            zf.writestr(f"Tayyor_{f.name}", excel_out.getvalue())
    return zip_buffer.getvalue()
