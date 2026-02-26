def find_smart_price(base_price, pack_size):
    if pack_size <= 0: pack_size = 1
    unit_cost = base_price / pack_size
    
    # 1. 12% dan 18% gacha tekshirish (100 so'mga aniq bo'linishini qidiradi)
    for p in range(120, 181):
        pct = p / 10.0
        sale_price = unit_cost * (1 + pct / 100)
        # Agar narx 100 ga roppa-rosa bo'linsa
        if round(sale_price, 2) % 100 == 0:
            return pct, int(sale_price)
            
    # 2. Agar topilmasa, STABIL 12% qo'shish va faqat 100 gacha TEPAGA yaxlitlash
    actual_12_percent = unit_cost * 1.12
    # 7116 bo'lsa -> 7200 bo'ladi. 10000 bo'lib ketmaydi!
    final_price = math.ceil(actual_12_percent / 100) * 100
    
    return 12.0, int(final_price)
