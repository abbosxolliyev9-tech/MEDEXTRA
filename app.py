def find_smart_price(base_price, pack_size):
    """12% dan 18% gacha optimal yaxlit narxni topish"""
    if pack_size <= 0: pack_size = 1
    unit_cost = base_price / pack_size
    
    # 1. 12.0% dan 18.0% gacha chiroyli (00) narxni qidirish
    for p in range(120, 181):
        pct = p / 10.0
        sale_price = unit_cost * (1 + pct / 100)
        
        # Agar narx roppa-rosa 100 so'mga bo'linsa
        if round(sale_price, 2) % 100 == 0:
            return pct, int(sale_price)
            
    # 2. Agar chiroyli narx topilmasa, 12% qo'shib TEPAga yaxlitlaymiz
    # (Matematik ceil ishlatamiz, 7116 -> 7200 bo'lishi uchun)
    import math
    min_sale_price = unit_cost * 1.12
    final_price = math.ceil(min_sale_price / 100) * 100
    
    return 12.0, final_price
