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

def get_floor_category_excel(floor_val, total_floor_val, is_housing=False, address_str=""):
    """
    엑셀 매물원장(거래사례) 층수대 산식:
    - 주택: 지하(B1), 저층(층비율 <= 20%), 중층(<= 60%), 고층(> 60%)
    - 상가: 1층(1층), 지하(B1), 저층(전체층 < 6층 또는 층비율 <= 40%), 중층(<= 70%), 고층(> 70%)
    """
    try:
        f_str = str(floor_val).upper().strip()
        t_str = str(total_floor_val).strip()
        addr_upper = str(address_str).upper()
        
        b1_keywords = ["B1", "B01", "B02", "지1층", "지2층", "지층", "지하", "지1층비", "지1", "B1층", "B2층"]
        if any(k in f_str for k in b1_keywords) or any(k in addr_upper for k in b1_keywords):
            return "B1"
            
        f_match = re.search(r'\d+', f_str)
        floor = int(f_match.group()) if f_match else 1
        
        t_match = re.search(r'\d+', t_str)
        total_floor = int(t_match.group()) if t_match else 5
        if total_floor <= 0:
            total_floor = 5
            
        ratio = floor / float(total_floor)
        
        if is_housing:
            if ratio <= 0.2:
                return "저"
            elif ratio <= 0.6:
                return "중"
            else:
                return "고"
        else:
            if floor == 1 or "1층" in f_str:
                return "1층"
            if total_floor < 6:
                return "저"
            if ratio <= 0.4:
                return "저"
            elif ratio <= 0.7:
                return "중"
            else:
                return "고"
    except Exception:
        return "저"

def get_area_category_excel(area_pyeong):
    """
    엑셀 매물원장(거래사례) 평수대 산식:
    - < 16평 -> 10 (10평이내)
    - < 26평 -> 20 (20평이내)
    - < 36평 -> 30 (30평이내)
    - >= 36평 -> 40 (40평이상)
    """
    try:
        area = float(area_pyeong)
        if area < 16:
            return 10
        elif area < 26:
            return 20
        elif area < 36:
            return 30
        else:
            return 40
    except Exception:
        return 20

def get_age_category_excel(build_year):
    """
    엑셀 매물원장(거래사례) 경과연수대 산식:
    - < 11년 -> 10 (10년이내)
    - < 25년 -> 25 (25년이내)
    - >= 25년 -> 26 (26년이상)
    """
    current_year = datetime.now().year
    try:
        age = current_year - int(build_year)
    except Exception:
        age = 20
    if age < 11:
        return 10
    elif age < 25:
        return 25
    else:
        return 26

def get_floor_category(floor_str, total_floor_str, is_housing=False):
    return get_floor_category_excel(floor_str, total_floor_str, is_housing)

def get_area_category(area_pyeong):
    return get_area_category_excel(area_pyeong)

def get_age_category_from_text(text):
    if pd.isna(text):
        return 25
    text = str(text).replace(" ", "")
    if "10년이내" in text or "10년이하" in text:
        return 10
    if "30년이내" in text or "30년이하" in text or "25년이내" in text or "25년이하" in text:
        return 25
    return 26

def extract_price_total(val):
    try:
        val_str = str(val).replace(',', '').strip()
        v = float(val_str)
        if v > 1000000:  # 원 단위인 경우 만원 단위로 변환
            return v / 10000.0
        return v
    except Exception:
        return np.nan

# Global memory cache for preloaded dataframes
_DATASET_CACHE = {}

def get_cached_dataset(target_type):
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "네이버부동산")
    
    # Determine dataset key and filter criteria
    if any(k in target_type for k in ["아파트"]):
        cache_key = "아파트"
        keywords = ["아파트"]
    elif any(k in target_type for k in ["빌라", "다세대", "연립"]):
        cache_key = "빌라"
        keywords = ["빌라", "다세대", "연립"]
    elif any(k in target_type for k in ["오피스텔"]):
        cache_key = "오피스텔"
        keywords = ["오피스텔"]
    elif any(k in target_type for k in ["단독", "다가구"]):
        cache_key = "단독"
        keywords = ["단독", "다가구"]
    else:
        # 상가, 근린상가, 근린생활시설, 상가주택 등
        cache_key = "상가"
        keywords = ["상가"]

    # Dynamically find matching files
    files = []
    if os.path.exists(data_dir):
        for fn in os.listdir(data_dir):
            if (fn.endswith('.xlsx') or fn.endswith('.xlsm')) and not fn.startswith('~$'):
                if any(kw in fn for kw in keywords):
                    files.append(fn)

    if cache_key in _DATASET_CACHE:
        return _DATASET_CACHE[cache_key]
        
    pkl_cache_file = os.path.join(data_dir, f".cache_naver_{cache_key}.pkl")
    
    # Check if pkl cache is valid by comparing last modified time with source excel files
    cache_valid = False
    if os.path.exists(pkl_cache_file):
        cache_mtime = os.path.getmtime(pkl_cache_file)
        latest_file_mtime = 0
        for fn in files:
            fp = os.path.join(data_dir, fn)
            if os.path.exists(fp):
                latest_file_mtime = max(latest_file_mtime, os.path.getmtime(fp))
        if cache_mtime >= latest_file_mtime:
            cache_valid = True

    if cache_valid:
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
    is_housing = any(k in cache_key for k in ["아파트", "빌라", "다세대", "연립", "단독", "다가구"])
    df['floor_cat'] = df.apply(lambda row: get_floor_category_excel(row.get('층수', ''), row.get('전체층', ''), is_housing=is_housing), axis=1)
    
    area_col = '전용평형' if '전용평형' in df.columns else ('공급평형' if '공급평형' in df.columns else '전용면적')
    df['area_pyeong_val'] = pd.to_numeric(df[area_col], errors='coerce')
    df['area_cat'] = df['area_pyeong_val'].apply(get_area_category_excel)
    
    df['age_cat'] = df.get('보조설명', pd.Series(dtype=str)).apply(get_age_category_from_text)
    
    price_col = '매매가(보증금)' if '매매가(보증금)' in df.columns else ('금액' if '금액' in df.columns else df.columns[0])
    df['price_total'] = df[price_col].apply(extract_price_total)
    
    # Deal type & Jeonse total (if available)
    deal_col = '거래유형' if '거래유형' in df.columns else ''
    if deal_col and deal_col in df.columns:
        df['deal_type_val'] = df[deal_col].astype(str)
    else:
        df['deal_type_val'] = '매매'
        
    rent_col = '월세' if '월세' in df.columns else ''
    if rent_col and rent_col in df.columns:
        df['rent_val'] = pd.to_numeric(df[rent_col], errors='coerce').fillna(0)
    else:
        df['rent_val'] = 0.0

    # Calculate pyeong price (만원/평)
    df['pyeong_price'] = np.where(df['area_pyeong_val'] > 0, df['price_total'] / df['area_pyeong_val'], np.nan)
    
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

def analyze_price(target_lat, target_lon, target_type, target_area_pyeong, target_floor, target_total_floor, target_build_year, target_appraised_price, target_min_price, target_senior_debt, radius_meters=1000):
    df_all = get_cached_dataset(target_type)
    if df_all is None or len(df_all) == 0:
        return {"error": f"데이터셋을 로드할 수 없습니다: {target_type}"}
        
    is_housing = any(k in str(target_type) for k in ["아파트", "빌라", "다세대", "연립", "단독", "다가구", "주택"])
    
    # Target property categories (Excel 거래사례 시트 산식 100% 동일)
    # Pass floor text and full address or floor string for basement check
    target_floor_cat = get_floor_category_excel(target_floor, target_total_floor, is_housing=is_housing, address_str=str(target_floor))
    target_area_cat = get_area_category_excel(target_area_pyeong)
    target_age_cat = get_age_category_excel(target_build_year)
    
    try:
        target_area_pyeong = float(target_area_pyeong)
    except Exception:
        target_area_pyeong = 20.0
        
    try:
        v = float(target_min_price)
        target_min_price_val = v / 10000.0 if v > 1000000 else v
    except Exception:
        target_min_price_val = 0.0

    # Coarse BBox filter for fast distance computation
    bbox_lat_diff = (radius_meters / 1000.0) * 0.015
    bbox_lon_diff = (radius_meters / 1000.0) * 0.018
    min_lat, max_lat = target_lat - bbox_lat_diff, target_lat + bbox_lat_diff
    min_lon, max_lon = target_lon - bbox_lon_diff, target_lon + bbox_lon_diff
    
    # Guarantee deal_type_val exists in df_all
    if 'deal_type_val' not in df_all.columns:
        if '거래유형' in df_all.columns:
            df_all['deal_type_val'] = df_all['거래유형'].astype(str)
        else:
            df_all['deal_type_val'] = '매매'

    df = df_all[(df_all['위도'] >= min_lat) & (df_all['위도'] <= max_lat) & (df_all['경도'] >= min_lon) & (df_all['경도'] <= max_lon)].copy()
    if len(df) == 0:
        df = df_all.copy()
        
    # Calculate distances
    df['distance'] = df.apply(lambda row: haversine(target_lat, target_lon, row['위도'], row['경도']), axis=1)
    
    # Filtering logic according to Excel 거래사례:
    radius_used = int(radius_meters)
    special_rule_applied = False
    special_rule_msg = ""

    if target_floor_cat == 'B1':
        # 1. 지하층 매물이 존재하는지 체크
        b1_matched = df[(df['distance'] <= radius_used) & 
                        (df['area_cat'] == target_area_cat) & 
                        (df['floor_cat'] == 'B1')].copy()
        if len(b1_matched) >= 1:
            matched = b1_matched
        else:
            # 2. 지하 사례 매물 부재 시 1층 시세의 60% 반영!
            one_f_matched = df[(df['distance'] <= radius_used) & 
                               (df['area_cat'] == target_area_cat) & 
                               (df['floor_cat'] == '1층')].copy()
            if len(one_f_matched) == 0:
                one_f_matched = df[(df['distance'] <= radius_used) & 
                                   (df['floor_cat'] == '1층')].copy()
            matched = one_f_matched
            special_rule_applied = True
            special_rule_msg = "지하 사례 매물 부족으로 1층 시세의 60% 특례 적용됨"
    else:
        matched = df[(df['distance'] <= radius_used) & 
                     (df['area_cat'] == target_area_cat) & 
                     (df['floor_cat'] == target_floor_cat) & 
                     (df['age_cat'] == target_age_cat)].copy()
                 
    # Fallback 1: 완화 - 경과연수 조건 완화
    if len(matched) < 2:
        matched = df[(df['distance'] <= radius_used) & 
                     (df['area_cat'] == target_area_cat) & 
                     (df['floor_cat'] == target_floor_cat)].copy()

    # Fallback 2: 완화 - 층수 조건 완화
    if len(matched) < 2:
        matched = df[(df['distance'] <= radius_used) & 
                     (df['area_cat'] == target_area_cat)].copy()

    # Fallback 3: 완화 - 반경 내 전체
    if len(matched) == 0:
        matched = df[df['distance'] <= radius_used].copy()

    # Calculate statistics based on matched properties
    if len(matched) > 0 and 'pyeong_price' in matched.columns:
        valid_pp = matched['pyeong_price'].dropna()
        raw_avg_pp = float(valid_pp.mean()) if len(valid_pp) > 0 else 0.0
    else:
        raw_avg_pp = 0.0

    if special_rule_applied and target_floor_cat == 'B1':
        avg_pyeong_price = raw_avg_pp * 0.6  # 1층 매물시세의 60% 반영!
    else:
        avg_pyeong_price = raw_avg_pp

    # 🎯 추정 시세 (탁상감정가) = 평당가 평균 * 해당물건 전용평수 * 0.9 (90% 반영!)
    estimated_market_price = avg_pyeong_price * target_area_pyeong * 0.9  # 만원 단위
    
    # 📊 최저가율 = (경공매 최저가 / 추정 시세) * 100 (%)
    if estimated_market_price > 0 and target_min_price_val > 0:
        min_price_ratio = (target_min_price_val / estimated_market_price) * 100.0
    else:
        min_price_ratio = 0.0

    # 🏠 전세가 및 전세가율 산출 (매칭 매물 중 전세/월세 데이터가 있는 경우)
    if 'deal_type_val' in matched.columns:
        jeonse_matched = matched[matched['deal_type_val'].str.contains('전세|월세', na=False)]
    else:
        jeonse_matched = matched.iloc[0:0]
    if len(jeonse_matched) > 0:
        jeonse_pp = jeonse_matched['pyeong_price'].dropna()
        avg_jeonse_pyeong_price = float(jeonse_pp.mean()) if len(jeonse_pp) > 0 else 0.0
    else:
        avg_jeonse_pyeong_price = 0.0
        
    estimated_jeonse_price = avg_jeonse_pyeong_price * target_area_pyeong  # 만원 단위
    if estimated_market_price > 0 and estimated_jeonse_price > 0:
        jeonse_ratio = (estimated_jeonse_price / estimated_market_price) * 100.0
    else:
        jeonse_ratio = 0.0

    # Properties list formatting
    properties_list = []
    if len(matched) > 0:
        sorted_matched = matched.sort_values(by='distance', ascending=True).head(50)
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
            
            pyeong_val = row.get('area_pyeong_val', row.get('전용평형', ''))
            try:
                pyeong_float = float(pyeong_val)
                pyeong_str = f"{pyeong_float:.1f}평"
            except Exception:
                pyeong_str = f"{pyeong_val}평"
                
            p_val = float(row.get('price_total', 0))
            p_eon = round(p_val / 10000.0, 2)
            
            pp_val = float(row.get('pyeong_price', 0))
            
            properties_list.append({
                "address": addr[:35] + ('...' if len(addr) > 35 else ''),
                "deal_type": str(row.get('deal_type_val', '매매')),
                "floor_cat": row.get('floor_cat', floor_val),
                "floor_display": floor_display,
                "pyeong": pyeong_str,
                "price_total": p_val,
                "price_eon": p_eon,
                "pyeong_price": round(pp_val, 1),
                "distance": int(row.get('distance', 0))
            })

    return {
        "radius_used": radius_used,
        "matched_count": len(matched),
        "target_categories": {
            "type_label": "주택" if is_housing else "상가/근린",
            "floor": target_floor_cat,
            "area": f"{target_area_cat}평대",
            "age": f"{target_age_cat}년대"
        },
        "target_info": {
            "area_pyeong": round(target_area_pyeong, 1),
            "min_price_eon": round(target_min_price_val / 10000.0, 2),
            "min_price_man": round(target_min_price_val, 0)
        },
        "calculation_result": {
            "avg_pyeong_price": round(avg_pyeong_price, 1),
            "estimated_market_price": round(estimated_market_price, 0),
            "estimated_market_price_eon": round(estimated_market_price / 10000.0, 2),
            "min_price_ratio": round(min_price_ratio, 1),
            "avg_jeonse_pyeong_price": round(avg_jeonse_pyeong_price, 1),
            "estimated_jeonse_price": round(estimated_jeonse_price, 0),
            "estimated_jeonse_price_eon": round(estimated_jeonse_price / 10000.0, 2),
            "jeonse_ratio": round(jeonse_ratio, 1)
        },
        "properties": properties_list
    }
