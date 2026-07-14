import os

file_path = r'backend\naver_price_analyzer.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the filter logic
old_filter = """
    # Try 500m
    matched = filter_data(500)
    radius_used = 500
    
    # Expand to 1km if < 3
    if len(matched) < 3:
        matched = filter_data(1000)
        radius_used = 1000
"""

new_filter = """
    radius_used = 500
    matched = filter_data(radius_used)
    
    # Expand by 500m increments if <= 3 matches, up to a reasonable limit (e.g., 5000m)
    max_radius = 5000
    while len(matched) <= 3 and radius_used < max_radius:
        radius_used += 500
        matched = filter_data(radius_used)
"""
if old_filter in content:
    content = content.replace(old_filter, new_filter)

# Replace the fallback and output logic
old_output = """
    # Special rule for Villa Subterranean
    special_rule_applied = False
    if "빌라" in target_type and target_floor_cat == "지하" and len(matched) < 3:
        # Fallback to 1st floor 70%
        fallback = df[(df['distance'] <= 1000) & (df['area_cat'] == target_area_cat) & (df['floor_cat'] == "1층")]
        if len(fallback) > 0:
            median_price = fallback['price_per_pyeong'].median() * 0.7
            min_price = fallback['price_per_pyeong'].min() * 0.7
            special_rule_applied = True
            matched = fallback  # Just for count reporting, but actually we use fallback stats
        else:
            median_price = 0
            min_price = 0
    else:
        median_price = matched['price_per_pyeong'].median() if len(matched) > 0 else 0
        min_price = matched['price_per_pyeong'].min() if len(matched) > 0 else 0
        
    disparity_a_median = ((median_price - ind_a) / median_price * 100) if median_price > 0 else 0
    disparity_b_median = ((median_price - ind_b) / median_price * 100) if median_price > 0 else 0
    
    # Clean output for JSON
    if pd.isna(median_price): median_price = 0
    if pd.isna(min_price): min_price = 0
    
    return {
        "radius_used": radius_used,
        "matched_count": len(matched) if not special_rule_applied else len(fallback),
        "special_rule_applied": special_rule_applied,
        "target_categories": {
            "floor": target_floor_cat,
            "area": target_area_cat,
            "age": target_age_cat
        },
        "target_indicators": {
            "ind_a": ind_a,
            "ind_b": ind_b,
            "expense_per_pyeong": expense_per_pyeong
        },
        "market_prices": {
            "median_per_pyeong": median_price,
            "min_per_pyeong": min_price
        },
        "disparities": {
            "ind_a_vs_median": disparity_a_median,
            "ind_b_vs_median": disparity_b_median
        }
    }
"""

new_output = """
    # Special rule for Villa Subterranean
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
        min_price = matched['price_per_pyeong'].min() if len(matched) > 0 else 0
        
    disparity_a_median = ((median_price - ind_a) / median_price * 100) if median_price > 0 else 0
    disparity_b_median = ((median_price - ind_b) / median_price * 100) if median_price > 0 else 0
    disparity_a_avg = ((avg_price - ind_a) / avg_price * 100) if avg_price > 0 else 0
    disparity_b_avg = ((avg_price - ind_b) / avg_price * 100) if avg_price > 0 else 0
    
    # Clean output for JSON
    if pd.isna(median_price): median_price = 0
    if pd.isna(avg_price): avg_price = 0
    if pd.isna(min_price): min_price = 0
    
    # Prepare properties list
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
            })
    
    return {
        "radius_used": radius_used,
        "matched_count": len(matched),
        "special_rule_applied": special_rule_applied,
        "target_categories": {
            "floor": target_floor_cat,
            "area": target_area_cat,
            "age": target_age_cat
        },
        "target_indicators": {
            "ind_a": ind_a,
            "ind_b": ind_b,
            "expense_per_pyeong": expense_per_pyeong
        },
        "market_prices": {
            "median_per_pyeong": median_price,
            "avg_per_pyeong": avg_price,
            "min_per_pyeong": min_price,
            "median_90": median_price * 0.9,
            "avg_90": avg_price * 0.9
        },
        "disparities": {
            "ind_a_vs_median": disparity_a_median,
            "ind_b_vs_median": disparity_b_median,
            "ind_a_vs_avg": disparity_a_avg,
            "ind_b_vs_avg": disparity_b_avg
        },
        "properties": properties_list
    }
"""

if old_output in content:
    content = content.replace(old_output, new_output)
else:
    print("Warning: old output not found")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated analyzer successfully")
