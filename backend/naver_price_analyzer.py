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
            if data.get('documents'):
                doc = data['documents'][0]
                if doc.get('road_address'):
                    return doc['road_address']['address_name']
                elif doc.get('address'):
                    return doc['address']['address_name']
    except Exception:
        pass
    return ""

# Calculate Haversine distance in meters
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
        if "B" in str(floor_str).upper() or "지하" in str(floor_str):
            return "지하"
        if str(floor_str).strip() == "1" or "1층" in str(floor_str):
            return "1층"
        
        f_match = re.search(r'\d+', str(floor_str))
        if not f_match:
            return "저층"
        floor = int(f_match.group())
        
        t_match = re.search(r'\d+', str(total_floor_str))
        if not t_match:
            return "저층"
        total_floor = int(t_match.group())
        
        if total_floor < 5:
            return "저층"
            
        if floor <= total_floor / 3.0:
            return "저층"
        elif floor <= (total_floor * 2.0) / 3.0:
            return "중층"
        else:
            return "고층"
    except Exception:
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

def extract_price_total(val):
    try:
        val_str = str(val).replace(',', '').strip()
        return float(val_str) / 100000000.0
    except:
        return np.nan

# Global memory cache for preloaded dataframes
_DATASET_CACHE = {}

def get_cached_dataset(target_type):
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "네이버부동산")
    
    # Determine dataset key
    if "아파트" in target_type:
        cache_key = "아파트"
        files = [
            "네이버부동산_서울_아파트_20260706.xlsx",
            "네이버부동산_경기도_성남시_아파트_20260805.xlsx",
            "네이버부동산_경기도_아파트_Part1_(1~50000)_20260904.xlsx",
            "네이버부동산_경기도_아파트_Part2_(50001~100000)_20260904.xlsx",
            "네이버부동산_경기도_아파트_Part3_(100001~122613)_20260904.xlsx"
        ]
    elif "빌라" in target_type or "다세대" in target_type or "연립" in target_type:
        cache_key = "빌라"
        files = ["네이버부동산_서울_빌라_20260706.xlsx"]
    elif "오피스텔" in target_type:
        cache_key = "오피스텔"
        files = ["네이버부동산_서울_오피스텔_20260707.xlsx"]
    elif "단독" in target_type or "다가구" in target_type:
        cache_key = "단독"
        files = ["네이버부동산_서울_단독_20260708.xlsx"]
    else:
        # 상가, 근린상가, 근린생활시설, 상가주택 등 (서울 + 경기도 상가 통합)
        cache_key = "상가"
        files = ["네이버부동산_서울_상가_20260706.xlsx", "네이버부동산_경기도_상가_20260819.xlsx"]
        
    if cache_key in _DATASET_CACHE:
        return _DATASET_CACHE[cache_key]
        
    pkl_cache_file = os.path.join(data_dir, f".cache_naver_{cache_key}.pkl")
    if os.path.exists(pkl_cache_file):
        try:
            import pickle
            with open(pkl_cache_file, "rb") as pf:
                cached_df = pickle.load(pf)
                _DATASET_CACHE[cache_key] = cached_df
                return cached_df
        except Exception as e:
            print(f"Pickle cache load failed for {cache_key}: {e}")

    df_list = []
    for fn in files:
        fp = os.path.join(data_dir, fn)
        if os.path.exists(fp):
            try:
                try:
                    sub_df = pd.read_excel(fp, engine="calamine")
                except Exception:
                    sub_df = pd.read_excel(fp)
                df_list.append(sub_df)
            except Exception as e:
                print(f"Error loading {fn}: {e}")
                
    if not df_list:
        return None
        
    df = pd.concat(df_list, ignore_index=True)
    
    # Drop rows without lat/lng
    df = df.dropna(subset=['위도', '경도'])
    df['위도'] = pd.to_numeric(df['위도'], errors='coerce')
    df['경도'] = pd.to_numeric(df['경도'], errors='coerce')
    df = df[(df['위도'] > 0) & (df['경도'] > 0)]
    
    # Pre-calculate categories
    df['floor_cat'] = df.apply(lambda row: get_floor_category(row.get('층수', ''), row.get('전체층', '')), axis=1)
    df['area_cat'] = df.get('전용평형', pd.Series(dtype=float)).apply(get_area_category)
    df['age_cat'] = df.get('보조설명', pd.Series(dtype=str)).apply(get_age_category_from_text)
    
    price_col = '매매가(보증금)' if '매매가(보증금)' in df.columns else ('금액' if '금액' in df.columns else df.columns[0])
    df['price_total'] = df[price_col].apply(extract_price_total)
    
    # Drop items where price_total is nan or <= 0
    df = df[df['price_total'] > 0]
    
    try:
        import pickle
        with open(pkl_cache_file, "wb") as pf:
            pickle.dump(df, pf, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        print(f"Failed to save pickle cache for {cache_key}: {e}")

    _DATASET_CACHE[cache_key] = df
    return df

def analyze_price(target_lat, target_lon, target_type, target_area_pyeong, target_floor, target_total_floor, target_build_year, target_appraised_price, target_min_price, target_senior_debt):
    df_all = get_cached_dataset(target_type)
    if df_all is None or len(df_all) == 0:
        return {"error": f"데이터셋을 로드할 수 없습니다: {target_type}"}
        
    # Coarse BBox filter (approx 10km radius ~ 0.1 deg) to boost speed
    bbox_lat_diff = 0.15
    bbox_lon_diff = 0.15
    min_lat, max_lat = target_lat - bbox_lat_diff, target_lat + bbox_lat_diff
    min_lon, max_lon = target_lon - bbox_lon_diff, target_lon + bbox_lon_diff
    
    df = df_all[(df_all['위도'] >= min_lat) & (df_all['위도'] <= max_lat) & (df_all['경도'] >= min_lon) & (df_all['경도'] <= max_lon)].copy()
    if len(df) == 0:
        # fallback to all
        df = df_all.copy()
        
    # Calculate distances
    df['distance'] = df.apply(lambda row: haversine(target_lat, target_lon, row['위도'], row['경도']), axis=1)
    
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
    except Exception:
        ind_a = 0
        ind_b = 0
        total_expense = 0
        
    # Filtering logic
    def filter_data(radius):
        filtered = df[df['distance'] <= radius].copy()
        filtered = filtered[filtered['area_cat'] == target_area_cat]
        if "빌라" in target_type and target_floor_cat == "지하":
            filtered = filtered[filtered['floor_cat'] == "지하"]
        else:
            filtered = filtered[filtered['floor_cat'] == target_floor_cat]
        
        filtered_age = filtered[filtered['age_cat'] == target_age_cat]
        if len(filtered_age) >= 3:
            return filtered_age
        return filtered

    radius_used = 500
    matched = filter_data(radius_used)
    
    # Expand by 500m increments if <= 3 matches, up to 5000m
    max_radius = 5000
    while len(matched) <= 3 and radius_used < max_radius:
        radius_used += 500
        matched = filter_data(radius_used)
        
    # If still empty or very few, relax floor condition if not basement villa
    if len(matched) == 0 and not ("빌라" in target_type and target_floor_cat == "지하"):
        matched = df[(df['distance'] <= radius_used) & (df['area_cat'] == target_area_cat)]
        if len(matched) == 0:
            matched = df[df['distance'] <= radius_used]
        
    # Special rule for Villa Subterranean
    special_rule_applied = False
    if "빌라" in target_type and target_floor_cat == "지하" and len(matched) <= 3:
        fallback = df[(df['distance'] <= radius_used) & (df['area_cat'] == target_area_cat) & (df['floor_cat'] == "1층")]
        if len(fallback) > 0:
            median_price = fallback['price_total'].median() * 0.7
            avg_price = fallback['price_total'].mean() * 0.7
            min_price = fallback['price_total'].min() * 0.7
            special_rule_applied = True
            matched = fallback
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
    
    properties_list = []
    if len(matched) > 0:
        sorted_matched = matched.sort_values(by='price_total', ascending=True).head(50)
        for _, row in sorted_matched.iterrows():
            loc = row.get('매물위치(주소)', '')
            addr = str(loc) if pd.notnull(loc) else ''
            
            lat = row.get('위도')
            lon = row.get('경도')
            if pd.notnull(lat) and pd.notnull(lon) and (not addr or addr == 'nan'):
                kakao_addr = get_kakao_address(lat, lon)
                if kakao_addr:
                    addr = kakao_addr
                    
            floor_val = row.get('층수', '')
            total_floor_val = row.get('전체층', '')
            floor_display = f"{floor_val}층" if pd.notnull(floor_val) and str(floor_val).strip() else ""
            if pd.notnull(total_floor_val) and str(total_floor_val).strip():
                floor_display += f" / {total_floor_val}층"
            
            pyeong_val = row.get('전용평형', row.get('공급평형', ''))
            pyeong_str = f"{float(pyeong_val):.1f}" if (pd.notnull(pyeong_val) and str(pyeong_val).replace('.','').isdigit()) else str(pyeong_val)
            
            properties_list.append({
                "address": addr[:35] + ('...' if len(addr) > 35 else ''),
                "floor_cat": row.get('floor_cat', floor_val),
                "floor_display": floor_display,
                "pyeong": pyeong_str,
                "price": round(float(row.get('price_total', 0)) * (0.7 if special_rule_applied else 1.0), 2),
                "distance": int(row.get('distance', 0))
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
            "ind_a": round(ind_a, 2),
            "ind_b": round(ind_b, 2),
            "total_expense": round(total_expense, 0)
        },
        "market_prices": {
            "median_price": round(median_price, 2),
            "avg_price": round(avg_price, 2),
            "min_price": round(min_price, 2),
            "median_90": round(median_price * 0.9, 2),
            "avg_90": round(avg_price * 0.9, 2)
        },
        "disparities": {
            "ind_a_vs_median": round(disparity_a_median, 2),
            "ind_b_vs_median": round(disparity_b_median, 2),
            "ind_a_vs_avg": round(disparity_a_avg, 2),
            "ind_b_vs_avg": round(disparity_b_avg, 2)
        },
        "properties": properties_list
    }
