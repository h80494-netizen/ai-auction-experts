import pandas as pd
import numpy as np
import os
import math
import re
from datetime import datetime
import requests

def get_kakao_address(lat, lon):
    try:
        url = f"https://dapi.kakao.com/v2/local/geo/coord2address.json?x={lon}&y={lat}"
        headers = {"Authorization": "KakaoAK 9e5265220f87e54e4379077cb60071bb"}
        response = requests.get(url, headers=headers, timeout=2)
        if response.status_code == 200:
            data = response.json()
            if data['documents']:
                doc = data['documents'][0]
                if doc.get('road_address'):
                    return doc['road_address']['address_name']
                elif doc.get('address'):
                    return doc['address']['address_name']
    except Exception:
        pass
    return ""

# Calculate Haversine distance
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Radius of earth in meters
    phi_1 = math.radians(lat1)
    phi_2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi_1) * math.cos(phi_2) * \
        math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    meters = R * c
    return meters

def get_floor_category(floor_str, total_floor_str):
    try:
        # Check for basement
        if "B" in str(floor_str).upper() or "지하" in str(floor_str):
            return "지하"
        if str(floor_str).strip() == "1" or "1층" in str(floor_str):
            return "1층"
        
        # Parse numeric floor
        f_match = re.search(r'\d+', str(floor_str))
        if not f_match:
            return "저층"
        floor = int(f_match.group())
        
        t_match = re.search(r'\d+', str(total_floor_str))
        if not t_match:
            return "저층"
        total_floor = int(t_match.group())
        
        if total_floor < 5:
            # If total floors < 5, and it's not B or 1st floor (handled above), it's '저층'
            return "저층"
            
        if floor <= total_floor / 3.0:
            return "저층"
        elif floor <= (total_floor * 2.0) / 3.0:
            return "중층"
        else:
            return "고층"
    except Exception as e:
        return "저층"

def get_area_category(area_pyeong):
    try:
        area = float(area_pyeong)
        if area <= 15:
            return "소형"
        elif area <= 30:
            return "중형"
        else:
            return "대형"
    except:
        return "중형"

def get_age_category_from_text(text):
    if pd.isna(text):
        return "알수없음"
    text = str(text).replace(" ", "")
    if "10년이내" in text or "10년이하" in text:
        return "10년이하"
    if "30년이내" in text or "30년이하" in text or "25년이내" in text or "25년이하" in text:
        return "30년이하"
    if "30년초과" in text or "30년이상" in text or "25년이상" in text or "25년초과" in text:
        return "30년초과"
    return "알수없음"

def analyze_price(target_lat, target_lon, target_type, target_area_pyeong, target_floor, target_total_floor, target_build_year, target_appraised_price, target_min_price, target_senior_debt):
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "네이버부동산")
    
    if "아파트" in target_type:
        file_path = os.path.join(data_dir, "네이버부동산_서울_아파트_20260706.xlsx")
    elif "빌라" in target_type or "다세대" in target_type:
        file_path = os.path.join(data_dir, "네이버부동산_서울_빌라_20260706.xlsx")
    else:
        file_path = os.path.join(data_dir, "네이버부동산_서울_상가_20260706.xlsx")
        
    if not os.path.exists(file_path):
        return {"error": f"Data file not found: {file_path}"}
        
    df = pd.read_excel(file_path)
    
    # Calculate distances
    df['distance'] = df.apply(lambda row: haversine(target_lat, target_lon, row['위도'], row['경도']) if pd.notnull(row['위도']) and pd.notnull(row['경도']) else 999999, axis=1)
    
    # Categorize properties
    df['floor_cat'] = df.apply(lambda row: get_floor_category(row['층수'], row['전체층']), axis=1)
    df['area_cat'] = df['전용평형'].apply(get_area_category)
    df['age_cat'] = df['보조설명'].apply(get_age_category_from_text)
    
    # Extract total asking price in 억원 (100 million won)
    def extract_price_total(val):
        try:
            # Assuming '매매가(보증금)' is in raw won like 1200000000 based on inspection
            val_str = str(val).replace(',', '').strip()
            return float(val_str) / 100000000.0
        except:
            return np.nan
    df['price_total'] = df['매매가(보증금)'].apply(extract_price_total)
    
    # Target property categories
    target_floor_cat = get_floor_category(target_floor, target_total_floor)
    target_area_cat = get_area_category(target_area_pyeong)
    current_year = datetime.now().year
    try:
        target_age = current_year - int(target_build_year)
    except:
        target_age = 20  # default
        
    if target_age <= 10:
        target_age_cat = "10년이하"
        expense_ratio = 0.1
    elif target_age <= 30:
        target_age_cat = "30년이하"
        expense_ratio = 0.5
    else:
        target_age_cat = "30년초과"
        expense_ratio = 0.7
        
    expense_per_pyeong = 1500000 * expense_ratio
    
    # Target indicators in 억원
    try:
        target_area_pyeong = float(target_area_pyeong)
        total_expense = expense_per_pyeong * target_area_pyeong
        ind_a = (float(target_min_price) + total_expense) / 100000000.0
        ind_b = (float(target_appraised_price) - float(target_senior_debt) + total_expense) / 100000000.0
    except Exception as e:
        ind_a = 0
        ind_b = 0
        total_expense = 0
        
    # Filtering logic
    def filter_data(radius):
        filtered = df[df['distance'] <= radius].copy()
        # Same area category
        filtered = filtered[filtered['area_cat'] == target_area_cat]
        # Same floor category (for villa basement, strict match)
        if "빌라" in target_type and target_floor_cat == "지하":
            filtered = filtered[filtered['floor_cat'] == "지하"]
        else:
            filtered = filtered[filtered['floor_cat'] == target_floor_cat]
        
        # Age category match (if present in text)
        filtered_age = filtered[filtered['age_cat'] == target_age_cat]
        if len(filtered_age) >= 3:
            return filtered_age
        return filtered

    radius_used = 500
    matched = filter_data(radius_used)
    
    # Expand by 500m increments if <= 3 matches, up to a reasonable limit (e.g., 5000m)
    max_radius = 5000
    while len(matched) <= 3 and radius_used < max_radius:
        radius_used += 500
        matched = filter_data(radius_used)
        
    # Special rule for Villa Subterranean
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
        min_price = matched['price_total'].min() if len(matched) > 0 else 0
        
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
        sorted_matched = matched.sort_values(by='price_total', ascending=True).head(50)
        for _, row in sorted_matched.iterrows():
            loc = row.get('매물위치(주소)', '')
            addr = str(loc) if pd.notnull(loc) else ''
            
            lat = row.get('위도')
            lon = row.get('경도')
            if pd.notnull(lat) and pd.notnull(lon):
                kakao_addr = get_kakao_address(lat, lon)
                if kakao_addr:
                    addr = kakao_addr
                    
            floor_val = row.get('층수', '')
            total_floor_val = row.get('전체층', '')
            floor_display = f"{floor_val}층" if pd.notnull(floor_val) else ""
            if pd.notnull(total_floor_val) and total_floor_val:
                floor_display += f" / {total_floor_val}층"
            
            # extract dong/ho if present, or just use part of the name
            name = row.get('단지명') or row.get('매물 번호') or '매물'
            properties_list.append({
                "address": addr[:30] + ('...' if len(addr) > 30 else ''),
                "floor_cat": row.get('floor_cat', floor_val),
                "floor_display": floor_display,
                "pyeong": row.get('전용평형', ''),
                "price": row.get('price_total', 0) * (0.7 if special_rule_applied else 1.0)
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
            "total_expense": total_expense
        },
        "market_prices": {
            "median_price": median_price,
            "avg_price": avg_price,
            "min_price": min_price,
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
