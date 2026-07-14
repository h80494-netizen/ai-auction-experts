import os

file_path = r'backend\naver_price_analyzer.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update price extraction
old_price = """    # Extract unit price (price per pyeong)
    def extract_price_per_pyeong(val):
        try:
            return float(str(val).replace(',', '')) * 10000  # Usually in 10,000 KRW
        except:
            return np.nan
    df['price_per_pyeong'] = df['전용평단가'].apply(extract_price_per_pyeong)"""
new_price = """    # Extract total asking price in 억원 (100 million won)
    def extract_price_total(val):
        try:
            # Assuming '매매가(보증금)' is in raw won like 1200000000 based on inspection
            val_str = str(val).replace(',', '').strip()
            return float(val_str) / 100000000.0
        except:
            return np.nan
    df['price_total'] = df['매매가(보증금)'].apply(extract_price_total)"""
if old_price in content:
    content = content.replace(old_price, new_price)

# 2. Update Indicators
old_ind = """    # Target indicators
    try:
        target_area_pyeong = float(target_area_pyeong)
        ind_a = (float(target_min_price) / target_area_pyeong) + expense_per_pyeong
        ind_b = ((float(target_appraised_price) - float(target_senior_debt)) / target_area_pyeong) + expense_per_pyeong
    except Exception as e:
        ind_a = 0
        ind_b = 0"""
new_ind = """    # Target indicators in 억원
    try:
        target_area_pyeong = float(target_area_pyeong)
        total_expense = expense_per_pyeong * target_area_pyeong
        ind_a = (float(target_min_price) + total_expense) / 100000000.0
        ind_b = (float(target_appraised_price) - float(target_senior_debt) + total_expense) / 100000000.0
    except Exception as e:
        ind_a = 0
        ind_b = 0
        total_expense = 0"""
if old_ind in content:
    content = content.replace(old_ind, new_ind)

# 3. Update the fallback logic (replace price_per_pyeong with price_total)
old_fallback = """    # Special rule for Villa Subterranean
    special_rule_applied = False
    if "빌라" in target_type and target_floor_cat == "지하" and len(matched) <= 3:
        # Fallback to 1st floor 70% within current expanded radius
        fallback = df[(df['distance'] <= radius_used) & (df['area_cat'] == target_area_cat) & (df['floor_cat'] == "1층")]
        if len(fallback) > 0:
            median_price = fallback['price_per_pyeong'].median() * 0.7
            avg_price = fallback['price_per_pyeong'].mean() * 0.7
            min_price = fallback['price_per_pyeong'].min() * 0.7
            special_rule_applied = True
            matched = fallback  # use fallback listings for display
        else:
            median_price = 0
            avg_price = 0
            min_price = 0
    else:
        median_price = matched['price_per_pyeong'].median() if len(matched) > 0 else 0
        avg_price = matched['price_per_pyeong'].mean() if len(matched) > 0 else 0
        min_price = matched['price_per_pyeong'].min() if len(matched) > 0 else 0"""
new_fallback = """    # Special rule for Villa Subterranean
    special_rule_applied = False
    if "빌라" in target_type and target_floor_cat == "지하" and len(matched) <= 3:
        # Fallback to 1st floor 70% within current expanded radius
        fallback = df[(df['distance'] <= radius_used) & (df['area_cat'] == target_area_cat) & (df['floor_cat'] == "1층")]
        if len(fallback) > 0:
            median_price = fallback['price_total'].median() * 0.7
            avg_price = fallback['price_total'].mean() * 0.7
            min_price = fallback['price_total'].min() * 0.7
            special_rule_applied = True
            matched = fallback  # use fallback listings for display
        else:
            median_price = 0
            avg_price = 0
            min_price = 0
    else:
        median_price = matched['price_total'].median() if len(matched) > 0 else 0
        avg_price = matched['price_total'].mean() if len(matched) > 0 else 0
        min_price = matched['price_total'].min() if len(matched) > 0 else 0"""
if old_fallback in content:
    content = content.replace(old_fallback, new_fallback)

# 4. Update the properties list logic (replace price_per_pyeong with price_total)
old_prop = """    # Prepare properties list
    properties_list = []
    if len(matched) > 0:
        # sort by price
        sorted_matched = matched.sort_values(by='price_per_pyeong', ascending=True).head(50)
        for _, row in sorted_matched.iterrows():
            loc = row.get('매물위치(주소)', '')
            addr = str(loc) if pd.notnull(loc) else ''
            
            # extract dong/ho if present, or just use part of the name
            name = row.get('단지명') or row.get('매물 번호') or '매물'
            properties_list.append({
                "address": addr[:30] + ('...' if len(addr) > 30 else ''),
                "floor": row.get('층수', ''),
                "pyeong": row.get('전용평형', ''),
                "price": row.get('price_per_pyeong', 0) * (0.7 if special_rule_applied else 1.0)
            })"""
new_prop = """    # Prepare properties list
    properties_list = []
    if len(matched) > 0:
        # sort by price
        sorted_matched = matched.sort_values(by='price_total', ascending=True).head(50)
        for _, row in sorted_matched.iterrows():
            loc = row.get('매물위치(주소)', '')
            addr = str(loc) if pd.notnull(loc) else ''
            
            # extract dong/ho if present, or just use part of the name
            name = row.get('단지명') or row.get('매물 번호') or '매물'
            properties_list.append({
                "address": addr[:30] + ('...' if len(addr) > 30 else ''),
                "floor": row.get('층수', ''),
                "pyeong": row.get('전용평형', ''),
                "price": row.get('price_total', 0) * (0.7 if special_rule_applied else 1.0)
            })"""
if old_prop in content:
    content = content.replace(old_prop, new_prop)

# 5. Fix returned values inside return { target_indicators: { expense_per_pyeong: ... } }
content = content.replace('"expense_per_pyeong": expense_per_pyeong', '"total_expense": total_expense')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated python module")
