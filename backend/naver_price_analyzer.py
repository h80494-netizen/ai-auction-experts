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
        
        # 1. 지하 층수 정밀 판별 (B3, B2, B1, -1, -2, -3 ...)
        m_neg = re.match(r'^-\s*(\d+)', f_str)
        if m_neg:
            return f"B{m_neg.group(1)}"
        combined_text = f"{f_str} {addr_upper}"
        if re.search(r'(?:제\s*)?지하\s*3층?|B\s*0?3|지\s*3층?', combined_text):
            return "B3"
        if re.search(r'(?:제\s*)?지하\s*2층?|B\s*0?2|지\s*2층?', combined_text):
            return "B2"
        if re.search(r'(?:제\s*)?지하\s*1층?|B\s*0?1|지\s*1층?|지층|지하', combined_text):
            return "B1"
        b_deep = re.search(r'(?:제\s*)?지하\s*(\d+)층?|B\s*0?(\d+)', combined_text)
        if b_deep:
            fl_num = b_deep.group(1) or b_deep.group(2)
            if fl_num:
                return f"B{fl_num}"
            
        # 한글 고/중/저 표기 매물 정밀 처리 (예: 고/25층, 중/18층, 저/15층)
        if f_str.startswith('고'):
            return "고"
        if f_str.startswith('중'):
            return "중"
        if f_str.startswith('저'):
            return "저"

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

def get_area_category_excel(area_pyeong, is_commercial=False):
    """
    평수대 분류 산식:
    - 상가(is_commercial=True):
      * <= 15평 -> 15 (소: 15평 이하)
      * <= 30평 -> 30 (중: 30평 이하)
      * >  30평 -> 31 (대: 30평 이상)
    - 주택/기타(is_commercial=False):
      * < 16평 -> 10 (10평대)
      * < 26평 -> 20 (20평대)
      * < 36평 -> 30 (30평대)
      * >= 36평 -> 40 (40평대)
    """
    if isinstance(area_pyeong, str):
        s = area_pyeong.replace(" ", "")
        if is_commercial:
            if s in ("소", "15평이하") or "소(" in s or "15평이하" in s:
                return 15
            if s in ("중", "30평이하") or "중(" in s or "30평이하" in s:
                return 30
            if s in ("대", "30평이상", "30평초과") or "대(" in s or "30평이상" in s or "30평초과" in s:
                return 31
        else:
            if "10평대" in s or s == "소" or "소(" in s:
                return 10
            if "20평대" in s or s == "중" or "중(" in s:
                return 20
            if "30평대" in s:
                return 30
            if "40평대" in s or s == "대" or "대(" in s:
                return 40
    try:
        area = float(area_pyeong)
        if math.isnan(area):
            return 30 if is_commercial else 20
        if is_commercial:
            if area <= 15:
                return 15
            elif area <= 30:
                return 30
            else:
                return 31
        else:
            if area < 16:
                return 10
            elif area < 26:
                return 20
            elif area < 36:
                return 30
            else:
                return 40
    except Exception:
        return 30 if is_commercial else 20


def format_area_category_label(area_cat, is_commercial=False):
    if is_commercial:
        if area_cat == 15:
            return "소 (15평 이하)"
        elif area_cat == 30:
            return "중 (30평 이하)"
        else:
            return "대 (30평 이상)"
    return f"{area_cat}평대"

def calculate_building_age_info(build_year_or_text, current_year=2026):
    """
    건축년도/사용승인일자 또는 텍스트에서 경과연수 및 3단계 노후도 구분을 도출:
    - 10년 이내: 신축/준신축
    - 25년 이내: 중축/보통
    - 25년 이상: 구축/노후
    """
    if not current_year:
        current_year = datetime.now().year
        
    year = None
    explicit_group = None
    if isinstance(build_year_or_text, (int, float)) and not math.isnan(float(build_year_or_text)) and build_year_or_text > 1900:
        year = int(build_year_or_text)
    elif build_year_or_text:
        text = str(build_year_or_text).strip()
        text_compact = text.replace(" ", "")
        m = re.search(r'(19\d{2}|20\d{2})', text_compact)
        if m:
            year = int(m.group(1))
        elif any(k in text_compact for k in ["10년이내", "10년이하", "4년이내", "2년이내", "신축"]):
            explicit_group = "10년 이내"
        elif any(k in text_compact for k in ["25년이상", "30년이상", "구축", "노후"]):
            explicit_group = "25년 이상"
        elif any(k in text_compact for k in ["15년이내", "25년이내", "25년이하", "중축", "보통"]):
            explicit_group = "25년 이내"

    if year and year > 1900:
        age_years = max(0, current_year - year)
        if age_years <= 10:
            category_label = "10년 이내"
            badge_color = "#10b981"  # green
        elif age_years < 25:
            category_label = "25년 이내"
            badge_color = "#2563eb"  # blue
        else:
            category_label = "25년 이상"
            badge_color = "#64748b"  # gray
        
        display_str = f"{year}년식 ({age_years}년차·{category_label})"
        return {
            "year": year,
            "age_years": age_years,
            "category_label": category_label,
            "display": display_str,
            "badge_color": badge_color
        }
    elif explicit_group:
        badge_map = {
            "10년 이내": "#10b981",
            "25년 이내": "#2563eb",
            "25년 이상": "#64748b",
        }
        return {
            "year": None,
            "age_years": None,
            "category_label": explicit_group,
            "display": explicit_group,
            "badge_color": badge_map.get(explicit_group, "#2563eb")
        }
    else:
        return {
            "year": None,
            "age_years": None,
            "category_label": "25년 이내",
            "display": "25년 이내",
            "badge_color": "#2563eb"
        }

def get_age_category_excel(build_year):
    """
    엑셀 매물원장(거래사례) 경과연수대 산식:
    - <= 10년 -> 10 (10년이내)
    - <= 25년 -> 25 (25년이내)
    - > 25년 -> 26 (25년이상)
    """
    age_info = calculate_building_age_info(build_year)
    cat = age_info["category_label"]
    if cat == "10년 이내":
        return 10
    elif cat == "25년 이내":
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
    if not text or text.lower() == 'nan':
        return 25
    m = re.search(r'(19\d{2}|20\d{2})', text)
    if m:
        age = max(0, datetime.now().year - int(m.group(1)))
        if age <= 10:
            return 10
        elif age < 25:
            return 25
        else:
            return 26
    if any(k in text for k in ["10년이내", "10년이하", "4년이내", "2년이내", "신축"]):
        return 10
    if any(k in text for k in ["25년이상", "30년이상", "구축", "노후"]):
        return 26
    if any(k in text for k in ["15년이내", "25년이내", "25년이하", "30년이내", "30년이하"]):
        return 25
    return 25

def extract_price_total(val, rent_val=0, deal_type=""):
    try:
        if pd.isna(val):
            return np.nan
        val_str = str(val).replace(',', '').strip()
        if not val_str or val_str.lower() in ('nan', 'none', '-'):
            return np.nan
        v = float(val_str)
        if math.isnan(v) or v <= 0:
            return np.nan
        deposit_man = v / 10000.0 if v > 1000000 else v
        
        if pd.isna(rent_val):
            rent_man = 0.0
        else:
            r_str = str(rent_val).replace(',', '').replace('만', '').strip()
            if not r_str or r_str.lower() in ('nan', 'none', '-'):
                rent_man = 0.0
            else:
                try:
                    rent_man = float(r_str)
                    if math.isnan(rent_man) or rent_man < 0:
                        rent_man = 0.0
                except Exception:
                    rent_man = 0.0
            
        deal_clean = str(deal_type).strip()
        if rent_man > 0 or deal_clean in ['월세', '전세', '전월세', '단기임대']:
            # 환산보증금 = 보증금(만원) + (월세(만원) * 100)
            return deposit_man + (rent_man * 100.0)
        return deposit_man
    except Exception:
        return np.nan

# Global memory cache for preloaded dataframes
_DATASET_CACHE = {}

def get_cached_dataset(target_type):
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "네이버부동산")
    os.makedirs(data_dir, exist_ok=True)
    
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
    elif any(k in target_type for k in ["토지", "대지", "임야", "잡종지"]):
        cache_key = "토지"
        keywords = ["토지", "대지"]
    else:
        # 상가, 근린상가, 근린생활시설, 상가주택 등
        cache_key = "상가"
        keywords = ["상가", "근린"]

    # 1. 메모리 캐시 확인
    if cache_key in _DATASET_CACHE:
        return _DATASET_CACHE[cache_key]

    pkl_cache_file = os.path.join(data_dir, f".cache_naver_v2_{cache_key}.pkl")
    if os.path.exists(pkl_cache_file):
        try:
            import pickle
            with open(pkl_cache_file, "rb") as pf:
                cached_df = pickle.load(pf)
                _DATASET_CACHE[cache_key] = cached_df
                return cached_df
        except Exception as e:
            print(f"Pickle cache load failed for {cache_key}: {e}")

    # 2. SQLite DB (map_data.db) 직결 로드 시도 (엑셀 파싱 대비 100배 고속)
    db_path = os.path.join(os.path.dirname(__file__), "data", "map_data.db")
    if os.path.exists(db_path):
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            type_cond = ""
            if cache_key == "아파트":
                type_cond = "estate_type = '아파트'"
            elif cache_key == "빌라":
                type_cond = "estate_type LIKE '%다세대%' OR estate_type LIKE '%빌라%'"
            elif cache_key == "오피스텔":
                type_cond = "estate_type LIKE '%오피스텔%'"
            elif cache_key == "단독":
                type_cond = "estate_type LIKE '%단독%'"
            elif cache_key == "토지":
                type_cond = "estate_type LIKE '%토지%'"
            else:
                type_cond = "estate_type LIKE '%상가%' OR estate_type LIKE '%근린%'"

            sql = f"""
                SELECT address as '소재지', address as '매물위치(주소)', price as '매매가(보증금)', rent as '월세',
                       floor as '층수', area as '전용면적_m2', deal_type as '거래유형',
                       type_detail as '매물명', lat as '위도', lng as '경도', age_info as '보조설명'
                FROM naver_real_estate
                WHERE ({type_cond}) AND lat > 0 AND lng > 0
            """
            db_df = pd.read_sql_query(sql, conn)
            conn.close()

            if not db_df.empty:
                # 층수 분리 (예: 5/10 -> 층수: 5, 전체층: 10)
                fl_nums = []
                fl_totals = []
                for raw_fl in db_df['층수'].tolist():
                    f_str = str(raw_fl or '')
                    if '/' in f_str:
                        parts = f_str.split('/', 1)
                        fl_nums.append(parts[0].strip())
                        fl_totals.append(parts[1].strip())
                    else:
                        fl_nums.append(f_str.strip())
                        fl_totals.append('')
                db_df['층수_num'] = fl_nums
                db_df['전체층'] = fl_totals

                is_housing = any(k in cache_key for k in ["아파트", "빌라", "다세대", "연립", "단독", "다가구", "오피스텔"])
                db_df['floor_cat'] = [
                    get_floor_category_excel(fn, tf, is_housing=is_housing)
                    for fn, tf in zip(fl_nums, fl_totals)
                ]

                # DB의 area 컬럼은 전용면적(㎡) 단위로 저장되므로 평(÷3.305785)으로 정밀 환산
                area_m2 = pd.to_numeric(db_df['전용면적_m2'], errors='coerce')
                db_df['area_pyeong_val'] = (area_m2 / 3.305785).round(2)
                db_df['전용평형'] = db_df['area_pyeong_val']
                ap = db_df['area_pyeong_val']
                is_comm_ds = (cache_key == "상가")
                if is_comm_ds:
                    db_df['area_cat'] = np.select(
                        [ap.isna(), ap <= 15, ap <= 30],
                        [30, 15, 30],
                        default=31
                    )
                else:
                    db_df['area_cat'] = np.select(
                        [ap.isna(), ap < 16, ap < 26, ap < 36],
                        [20, 10, 20, 30],
                        default=40
                    )
                db_df['age_cat'] = [get_age_category_from_text(x) for x in db_df['보조설명'].tolist()]

                p_num = pd.to_numeric(
                    db_df['매매가(보증금)'].astype(str).str.replace(',', '', regex=False).str.strip(),
                    errors='coerce'
                )
                dep_man = np.where(p_num > 1000000, p_num / 10000.0, p_num)
                r_num = pd.to_numeric(
                    db_df['월세'].astype(str).str.replace(',', '', regex=False).str.replace('만', '', regex=False).str.strip(),
                    errors='coerce'
                ).fillna(0.0)
                r_num = np.where(r_num > 0, r_num, 0.0)
                deal_s = db_df['거래유형'].fillna('').astype(str).str.strip()
                is_rental = (r_num > 0) | deal_s.isin(['월세', '전세', '전월세', '단기임대'])

                db_df['price_total'] = np.where(is_rental, dep_man + (r_num * 100.0), dep_man)
                db_df['deal_type_val'] = deal_s
                db_df['rent_val'] = r_num
                db_df['pyeong_price'] = np.where(db_df['area_pyeong_val'] > 0, db_df['price_total'] / db_df['area_pyeong_val'], np.nan)
                db_df = db_df[db_df['price_total'] > 0]

                try:
                    import pickle
                    with open(pkl_cache_file, "wb") as pf:
                        pickle.dump(db_df, pf, protocol=pickle.HIGHEST_PROTOCOL)
                except Exception as pe:
                    print(f"Failed to save pickle cache: {pe}")

                _DATASET_CACHE[cache_key] = db_df
                return db_df
        except Exception as dbe:
            print(f"Failed loading from DB for {cache_key}, fallback to excel: {dbe}")

    # 3. Fallback: 엑셀 파일 로드
    files = []
    if os.path.exists(data_dir):
        for fn in os.listdir(data_dir):
            if (fn.endswith('.xlsx') or fn.endswith('.xlsm') or fn.endswith('.csv')) and not fn.startswith('~$'):
                if any(kw in fn for kw in keywords):
                    files.append(fn)

    df_list = []
    for fn in files:
        fp = os.path.join(data_dir, fn)
        if os.path.exists(fp):
            try:
                if fn.endswith('.csv'):
                    try:
                        sub_df = pd.read_csv(fp, encoding='utf-8-sig')
                    except Exception:
                        try:
                            sub_df = pd.read_csv(fp, encoding='cp949')
                        except Exception:
                            sub_df = pd.read_csv(fp, encoding='euc-kr')
                else:
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
    is_housing = any(k in cache_key for k in ["아파트", "빌라", "다세대", "연립", "단독", "다가구", "오피스텔"])
    df['floor_cat'] = df.apply(lambda row: get_floor_category_excel(row.get('층수', ''), row.get('전체층', ''), is_housing=is_housing), axis=1)
    
    if '전용평형' in df.columns:
        df['area_pyeong_val'] = pd.to_numeric(df['전용평형'], errors='coerce')
    elif '전용면적' in df.columns:
        df['area_pyeong_val'] = (pd.to_numeric(df['전용면적'], errors='coerce') / 3.305785).round(2)
    elif '공급평형' in df.columns:
        df['area_pyeong_val'] = pd.to_numeric(df['공급평형'], errors='coerce')
    else:
        df['area_pyeong_val'] = np.nan
    is_comm_ds = (cache_key == "상가")
    df['area_cat'] = df['area_pyeong_val'].apply(lambda x: get_area_category_excel(x, is_commercial=is_comm_ds))
    
    df['age_cat'] = df.get('보조설명', pd.Series(dtype=str)).apply(get_age_category_from_text)
    
    price_col = '매매가(보증금)' if '매매가(보증금)' in df.columns else ('금액' if '금액' in df.columns else df.columns[0])
    rent_col = '월세' if '월세' in df.columns else ''
    deal_col = '거래유형' if '거래유형' in df.columns else ''

    df['price_total'] = df.apply(
        lambda r: extract_price_total(
            r.get(price_col, 0),
            r.get(rent_col, 0) if rent_col else 0,
            r.get(deal_col, '') if deal_col else ''
        ),
        axis=1
    )
    
    # Deal type & Jeonse total (if available)
    if deal_col and deal_col in df.columns:
        df['deal_type_val'] = df[deal_col].astype(str)
    else:
        df['deal_type_val'] = '매매'
        
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

def _transform_db_dataframe(db_df: pd.DataFrame, cache_key: str) -> pd.DataFrame:
    if db_df is None or db_df.empty:
        return pd.DataFrame()
    fl_nums = []
    fl_totals = []
    for raw_fl in db_df['층수'].tolist():
        f_str = str(raw_fl or '')
        if '/' in f_str:
            parts = f_str.split('/', 1)
            fl_nums.append(parts[0].strip())
            fl_totals.append(parts[1].strip())
        else:
            fl_nums.append(f_str.strip())
            fl_totals.append('')
    db_df['층수_num'] = fl_nums
    db_df['전체층'] = fl_totals

    is_housing = any(k in cache_key for k in ["아파트", "빌라", "다세대", "연립", "단독", "다가구", "오피스텔"])
    db_df['floor_cat'] = [
        get_floor_category_excel(fn, tf, is_housing=is_housing)
        for fn, tf in zip(fl_nums, fl_totals)
    ]

    area_m2 = pd.to_numeric(db_df['전용면적_m2'], errors='coerce')
    db_df['area_pyeong_val'] = (area_m2 / 3.305785).round(2)
    db_df['전용평형'] = db_df['area_pyeong_val']
    ap = db_df['area_pyeong_val']
    is_comm_ds = (cache_key == "상가")
    if is_comm_ds:
        db_df['area_cat'] = np.select(
            [ap.isna(), ap <= 15, ap <= 30],
            [30, 15, 30],
            default=31
        )
    else:
        db_df['area_cat'] = np.select(
            [ap.isna(), ap < 16, ap < 26, ap < 36],
            [20, 10, 20, 30],
            default=40
        )
    db_df['age_cat'] = [get_age_category_from_text(x) for x in db_df['보조설명'].tolist()]

    p_num = pd.to_numeric(
        db_df['매매가(보증금)'].astype(str).str.replace(',', '', regex=False).str.strip(),
        errors='coerce'
    )
    dep_man = np.where(p_num > 1000000, p_num / 10000.0, p_num)
    r_num = pd.to_numeric(
        db_df['월세'].astype(str).str.replace(',', '', regex=False).str.replace('만', '', regex=False).str.strip(),
        errors='coerce'
    ).fillna(0.0)
    r_num = np.where(r_num > 0, r_num, 0.0)
    deal_s = db_df['거래유형'].fillna('').astype(str).str.strip()
    is_rental = (r_num > 0) | deal_s.isin(['월세', '전세', '전월세', '단기임대'])

    # 환산보증금(만원) = 보증금(만원) + 월세(만원) * 100
    db_df['price_total'] = np.where(is_rental, dep_man + (r_num * 100.0), dep_man)
    db_df['deal_type_val'] = deal_s
    db_df['rent_val'] = r_num
    db_df['pyeong_price'] = np.where(db_df['area_pyeong_val'] > 0, db_df['price_total'] / db_df['area_pyeong_val'], np.nan)
    db_df = db_df[db_df['price_total'] > 0].copy()
    return db_df


def _query_bbox_from_db(target_type: str, min_lat: float, max_lat: float, min_lon: float, max_lon: float):
    db_path = os.path.join(os.path.dirname(__file__), "data", "map_data.db")
    if not os.path.exists(db_path):
        return None
    if any(k in str(target_type) for k in ["아파트"]):
        cache_key = "아파트"
        type_cond = "estate_type = '아파트'"
    elif any(k in str(target_type) for k in ["빌라", "다세대", "연립"]):
        cache_key = "빌라"
        type_cond = "estate_type LIKE '%다세대%' OR estate_type LIKE '%빌라%'"
    elif any(k in str(target_type) for k in ["오피스텔"]):
        cache_key = "오피스텔"
        type_cond = "estate_type LIKE '%오피스텔%'"
    elif any(k in str(target_type) for k in ["단독", "다가구"]):
        cache_key = "단독"
        type_cond = "estate_type LIKE '%단독%'"
    elif any(k in str(target_type) for k in ["토지", "대지", "임야", "잡종지"]):
        cache_key = "토지"
        type_cond = "estate_type LIKE '%토지%'"
    else:
        cache_key = "상가"
        type_cond = "estate_type LIKE '%상가%' OR estate_type LIKE '%근린%'"

    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        sql = f"""
            SELECT address as '소재지', address as '매물위치(주소)', price as '매매가(보증금)', rent as '월세',
                   floor as '층수', area as '전용면적_m2', deal_type as '거래유형',
                   type_detail as '매물명', lat as '위도', lng as '경도', age_info as '보조설명'
            FROM naver_real_estate
            WHERE ({type_cond})
              AND lat >= ? AND lat <= ?
              AND lng >= ? AND lng <= ?
        """
        db_df = pd.read_sql_query(sql, conn, params=[min_lat, max_lat, min_lon, max_lon])
        conn.close()
        if db_df is not None and not db_df.empty:
            return _transform_db_dataframe(db_df, cache_key)
        return pd.DataFrame()
    except Exception as e:
        print(f"BBox DB query warning ({cache_key}): {e}")
        return None


def analyze_price(target_lat, target_lon, target_type, target_area_pyeong, target_floor, target_total_floor, target_build_year, target_appraised_price, target_min_price, target_senior_debt, radius_meters=1000, commercial_zone_only=False, single_zone_geojson=None, area_group_override=None):
    is_land = any(k in str(target_type) for k in ["토지", "대지", "임야", "잡종지"])
    is_officetel = "오피스텔" in str(target_type)
    is_housing = (not is_land) and (not is_officetel) and any(k in str(target_type) for k in ["아파트", "빌라", "다세대", "연립", "단독", "다가구", "주택"])
    is_commercial = (not is_land) and (not is_housing) and (not is_officetel)
    
    # Target property categories
    target_floor_cat = "-" if is_land else get_floor_category_excel(target_floor, target_total_floor, is_housing=(is_housing or is_officetel), address_str=str(target_floor))
    area_cat_source = area_group_override if (area_group_override and str(area_group_override).strip() not in ("", "전체", "auto")) else target_area_pyeong
    target_area_cat = get_area_category_excel(area_cat_source, is_commercial=is_commercial)
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
    if single_zone_geojson:
        bbox_lat_diff = max(bbox_lat_diff, 0.04)
        bbox_lon_diff = max(bbox_lon_diff, 0.05)
    min_lat, max_lat = target_lat - bbox_lat_diff, target_lat + bbox_lat_diff
    min_lon, max_lon = target_lon - bbox_lon_diff, target_lon + bbox_lon_diff

    # 1순위: SQLite 공간 인덱스(BBox) 초고속 직결 조회 (메모리 점유 0, OOM 방지)
    df = _query_bbox_from_db(target_type, min_lat, max_lat, min_lon, max_lon)
    if df is not None and len(df) == 0:
        # 반경 내 매물이 없을 경우 광역 BBox로 1회 확장 탐색
        df = _query_bbox_from_db(target_type, target_lat - 0.15, target_lat + 0.15, target_lon - 0.18, target_lon + 0.18)

    if df is None:
        df_all = get_cached_dataset(target_type)
        if df_all is None or len(df_all) == 0:
            return {"error": f"데이터셋을 로드할 수 없습니다: {target_type}"}
        if 'deal_type_val' not in df_all.columns:
            if '거래유형' in df_all.columns:
                df_all['deal_type_val'] = df_all['거래유형'].astype(str)
            else:
                df_all['deal_type_val'] = '매매'
        df = df_all[(df_all['위도'] >= min_lat) & (df_all['위도'] <= max_lat) & (df_all['경도'] >= min_lon) & (df_all['경도'] <= max_lon)].copy()
        if len(df) == 0:
            df = df_all.copy()

    if df is None or len(df) == 0:
        return {"error": f"해당 지역 주변에 비교 가능한 {target_type} 시세 데이터가 없습니다."}
        
    # Vectorized Haversine distance calculation
    lat1_r = np.radians(target_lat)
    lon1_r = np.radians(target_lon)
    lat2_r = np.radians(df['위도'].to_numpy(dtype=float))
    lon2_r = np.radians(df['경도'].to_numpy(dtype=float))
    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1_r) * np.cos(lat2_r) * (np.sin(dlon / 2.0) ** 2)
    df['distance'] = 6371000.0 * 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
    
    # Filtering logic according to Excel 거래사례:
    radius_used = int(radius_meters)
    special_rule_applied = False
    special_rule_msg = ""
    commercial_zone_note = ""

    if commercial_zone_only or single_zone_geojson:
        try:
            from commercial_zone_analyzer import filter_df_by_commercial_zones
            df_cz, cz_msg = filter_df_by_commercial_zones(
                df[df['distance'] <= radius_used].copy() if not single_zone_geojson else df.copy(),
                min_lat, max_lat, min_lon, max_lon,
                single_geom=single_zone_geojson,
            )
            df = df_cz
            commercial_zone_note = cz_msg
            if single_zone_geojson:
                radius_used = 999999  # 폴리곤 내부 전체 대상
        except Exception as cze:
            print(f"Commercial zone filter warning: {cze}")

    is_basement = (not is_land) and str(target_floor_cat).startswith('B')

    def _has_sale_rows(sub_df):
        if sub_df is None or len(sub_df) == 0:
            return False
        if 'deal_type_val' in sub_df.columns:
            return bool(sub_df['deal_type_val'].str.contains('매매', na=False).any())
        return len(sub_df) > 0

    if is_land:
        matched = df[(df['distance'] <= radius_used) &
                     (df['area_cat'] == target_area_cat)].copy()
        if not _has_sale_rows(matched):
            matched = df[df['distance'] <= radius_used].copy()
    elif is_basement:
        # 1. 지하층 매물 탐색 (노후도·평수 일치 지하 -> 전체 지하 -> 1층 시세 60% 특례 순서)
        b_mask = df['floor_cat'].astype(str).str.startswith('B', na=False)
        b_exact_age = df[(df['distance'] <= radius_used) &
                         (df['area_cat'] == target_area_cat) &
                         b_mask &
                         (df['age_cat'] == target_age_cat)].copy()
        same_b_matched = df[(df['distance'] <= radius_used) & 
                            (df['area_cat'] == target_area_cat) & 
                            (df['floor_cat'] == target_floor_cat)].copy()
        all_b_matched = df[(df['distance'] <= radius_used) & 
                           (df['area_cat'] == target_area_cat) & 
                           b_mask].copy()
        any_b_matched = df[(df['distance'] <= radius_used) & b_mask].copy()

        if _has_sale_rows(b_exact_age):
            matched = b_exact_age
        elif _has_sale_rows(same_b_matched):
            matched = same_b_matched
        elif _has_sale_rows(all_b_matched):
            matched = all_b_matched
        elif _has_sale_rows(any_b_matched):
            matched = any_b_matched
        else:
            # 2. 지하 사례 매물 부재 시 1층 시세를 기준 매물로 활용
            one_f_matched = df[(df['distance'] <= radius_used) & 
                               (df['area_cat'] == target_area_cat) & 
                               (df['floor_cat'] == '1층')].copy()
            if len(one_f_matched) == 0:
                one_f_matched = df[(df['distance'] <= radius_used) & 
                                   (df['floor_cat'] == '1층')].copy()
            matched = one_f_matched
            special_rule_applied = True
    else:
        # 1차: 반경 + 평형대 + 층수군 + 건축연도 노후도 그룹(10년 이내 / 25년 이내 / 25년 이상) 정확 일치
        matched = df[(df['distance'] <= radius_used) & 
                     (df['area_cat'] == target_area_cat) & 
                     (df['floor_cat'] == target_floor_cat) & 
                     (df['age_cat'] == target_age_cat)].copy()

        # 2차: 건축연도 노후도 그룹(age_cat)을 최우선 유지하면서 층수/면적 조건만 단계적 완화
        if not _has_sale_rows(matched):
            if (not is_housing) and (not is_officetel) and target_floor_cat == '1층':
                # 상가 1층은 층별 시세 격차가 크므로 1층 + 동일 노후도 유지 후 면적 완화
                matched = df[(df['distance'] <= radius_used) &
                             (df['floor_cat'] == '1층') &
                             (df['age_cat'] == target_age_cat)].copy()
            elif (not is_housing) and (not is_officetel):
                upper_mask = (~df['floor_cat'].isin(['1층'])) & (~df['floor_cat'].astype(str).str.startswith('B'))
                matched = df[(df['distance'] <= radius_used) &
                             (df['area_cat'] == target_area_cat) &
                             upper_mask &
                             (df['age_cat'] == target_age_cat)].copy()
                if not _has_sale_rows(matched):
                    matched = df[(df['distance'] <= radius_used) &
                                 upper_mask &
                                 (df['age_cat'] == target_age_cat)].copy()
            else:
                ag_mask = ~df['floor_cat'].astype(str).str.startswith('B')
                matched = df[(df['distance'] <= radius_used) &
                             (df['area_cat'] == target_area_cat) &
                             ag_mask &
                             (df['age_cat'] == target_age_cat)].copy()
                if not _has_sale_rows(matched):
                    matched = df[(df['distance'] <= radius_used) &
                                 ag_mask &
                                 (df['age_cat'] == target_age_cat)].copy()

        # 3차 Fallback: 반경 내 선택 노후도 그룹 매매 사례가 전무할 때만 연식 조건 완화
        if not _has_sale_rows(matched):
            matched = df[(df['distance'] <= radius_used) & 
                         (df['area_cat'] == target_area_cat) & 
                         (df['floor_cat'] == target_floor_cat)].copy()

        if not _has_sale_rows(matched):
            matched = df[(df['distance'] <= radius_used) & 
                         (df['area_cat'] == target_area_cat)].copy()

        if len(matched) == 0:
            matched = df[df['distance'] <= radius_used].copy()

    # 🎯 1. 평균 평당가 산출: 오직 '매매' 매물만 필터링하여 계산 (월세, 전세 환산보증금 제외)
    if 'deal_type_val' in matched.columns:
        sale_matched = matched[matched['deal_type_val'].str.contains('매매', na=False)].copy()
    else:
        sale_matched = matched.copy()

    # 만약 해당 층/평형/연수 조건군 내 매매 매물이 부족한 경우, 동일 반경 내 매매 사례로 단계적 완화
    if len(sale_matched) == 0:
        if 'deal_type_val' in df.columns:
            # 1) 반경 내 동일 평형대 매매
            sale_fallback = df[(df['distance'] <= radius_used) & 
                               (df['area_cat'] == target_area_cat) & 
                               (df['deal_type_val'].str.contains('매매', na=False))].copy()
            # 2) 반경 내 전체 매매
            if len(sale_fallback) == 0:
                sale_fallback = df[(df['distance'] <= radius_used) & 
                                   (df['deal_type_val'].str.contains('매매', na=False))].copy()
            sale_matched = sale_fallback

    if len(sale_matched) > 0 and 'pyeong_price' in sale_matched.columns:
        valid_sale_pp = sale_matched['pyeong_price'].dropna()
        raw_avg_pp = float(valid_sale_pp.mean()) if len(valid_sale_pp) > 0 else 0.0
    else:
        raw_avg_pp = 0.0

    # 🎯 지하 층수별 가격 책정 규칙:
    # 지하 1층(B1): 1층 시세의 60%
    # 지하 2층, 지하 3층(B2, B3): 지하 1층 가격의 20% 적은 80% 수준으로 책정!
    if is_basement:
        if special_rule_applied:
            # 1층 매물 기준일 때:
            b1_base_price = raw_avg_pp * 0.6  # 1층의 60%
            if target_floor_cat in ['B2', 'B3', 'B4', 'B5']:
                avg_pyeong_price = b1_base_price * 0.8  # B1 가격의 80% (1층 시세의 48%)
                special_rule_msg = f"{target_floor_cat} 특례: 1층 시세 60%(B1 기준)의 80% 적용 (실제 48% 반영)"
            else:
                avg_pyeong_price = b1_base_price
                special_rule_msg = "지하 사례 매물 부족으로 1층 시세의 60% 특례 적용됨"
        else:
            # 지하 매물이 있는 경우:
            if target_floor_cat in ['B2', 'B3', 'B4', 'B5']:
                avg_pyeong_price = raw_avg_pp * 0.8  # B1 가격의 80% (20% 감가)
                special_rule_applied = True
                special_rule_msg = f"{target_floor_cat} 특례: 지하1층 시세의 80%(20% 감가) 적용"
            else:
                avg_pyeong_price = raw_avg_pp
    else:
        avg_pyeong_price = raw_avg_pp

    # 🎯 추정 시세 (탁상감정가) = 매매 평당가 평균 * 해당물건 전용평수 * 0.9 (90% 반영!)
    estimated_market_price = avg_pyeong_price * target_area_pyeong * 0.9  # 만원 단위
    
    # 📊 최저가율 = (경공매 최저가 / 추정 시세) * 100 (%)
    if estimated_market_price > 0 and target_min_price_val > 0:
        min_price_ratio = (target_min_price_val / estimated_market_price) * 100.0
    else:
        min_price_ratio = 0.0

    # 🏠 2. 전세가 및 전세가율 산출: 전월세 환산보증금(보증금 + 월세×100)을 구해
    #    전세가율(%) = (평당 환산보증금 / 평당 매매가) × 100 으로 산출
    if 'deal_type_val' in matched.columns:
        jeonse_matched = matched[matched['deal_type_val'].str.contains('전세|월세|단기임대', na=False)].copy()
    else:
        jeonse_matched = matched.iloc[0:0].copy()

    # 만약 조건군 내 전월세가 없으면 단계적 완화 탐색 (층·연식·평수 -> 연식·평수 -> 동일평형대 -> 반경 내 전체 전월세)
    if len(jeonse_matched) == 0 and 'deal_type_val' in df.columns:
        rent_pool = df[(df['distance'] <= radius_used) &
                       (df['deal_type_val'].str.contains('전세|월세|단기임대', na=False))].copy()
        if len(rent_pool) > 0:
            c1 = rent_pool[(rent_pool['area_cat'] == target_area_cat) &
                           (rent_pool['floor_cat'] == target_floor_cat) &
                           (rent_pool['age_cat'] == target_age_cat)]
            if len(c1) > 0:
                jeonse_matched = c1.copy()
            else:
                if is_basement:
                    c2 = rent_pool[(rent_pool['area_cat'] == target_area_cat) &
                                   (rent_pool['floor_cat'].astype(str).str.startswith('B')) &
                                   (rent_pool['age_cat'] == target_age_cat)]
                else:
                    c2 = rent_pool[(rent_pool['area_cat'] == target_area_cat) &
                                   (~rent_pool['floor_cat'].astype(str).str.startswith('B')) &
                                   (rent_pool['age_cat'] == target_age_cat)]
                if len(c2) > 0:
                    jeonse_matched = c2.copy()
                else:
                    c3 = rent_pool[rent_pool['area_cat'] == target_area_cat]
                    if len(c3) > 0:
                        jeonse_matched = c3.copy()
                    else:
                        jeonse_matched = rent_pool.copy()

    if len(jeonse_matched) > 0 and 'pyeong_price' in jeonse_matched.columns:
        jeonse_pp = jeonse_matched['pyeong_price'].dropna()
        avg_jeonse_pyeong_price = float(jeonse_pp.mean()) if len(jeonse_pp) > 0 else 0.0
    else:
        avg_jeonse_pyeong_price = 0.0
        
    estimated_jeonse_price = avg_jeonse_pyeong_price * target_area_pyeong  # 만원 단위 (환산보증금 기준)
    # 전세가율(%) = (평당 환산보증금 / 평당 매매가) × 100
    if avg_pyeong_price > 0 and avg_jeonse_pyeong_price > 0:
        jeonse_ratio = (avg_jeonse_pyeong_price / avg_pyeong_price) * 100.0
    else:
        jeonse_ratio = 0.0

    # Properties list formatting: 오직 '매매' 매물만 리스트에 표출 (월세, 전세는 전세가율 계산에만 사용)
    properties_list = []
    display_df = sale_matched if ('sale_matched' in locals() and len(sale_matched) > 0) else None
    if display_df is not None and len(display_df) > 0:
        sorted_matched = display_df.sort_values(by='distance', ascending=True).head(50)
        for _, row in sorted_matched.iterrows():
            loc = row.get('매물위치(주소)', '')
            if pd.isna(loc) or not str(loc).strip() or str(loc).strip() == 'nan':
                loc = row.get('소재지', '')
            addr = str(loc) if pd.notnull(loc) and str(loc).strip() != 'nan' else ''
            
            lat = row.get('위도')
            lon = row.get('경도')
            if pd.notnull(lat) and pd.notnull(lon) and (not addr or addr == 'nan'):
                kakao_addr = get_kakao_address(lat, lon)
                if kakao_addr:
                    addr = kakao_addr
                    
            floor_val = str(row.get('층수', '') or '').strip()
            total_floor_val = str(row.get('전체층', '') or '').strip()
            if '/' in floor_val and not total_floor_val:
                f_parts = floor_val.split('/')
                floor_val = f_parts[0].replace('층', '').strip()
                total_floor_val = f_parts[1].replace('층', '').strip()
            else:
                floor_val = floor_val.replace('층', '').strip()
                total_floor_val = total_floor_val.replace('층', '').strip()

            floor_display = f"{floor_val}층" if floor_val else ""
            if total_floor_val:
                floor_display = f"{floor_display} / {total_floor_val}층" if floor_display else f"{total_floor_val}층"
            
            pyeong_val = row.get('area_pyeong_val', row.get('전용평형', ''))
            try:
                pyeong_float = float(pyeong_val)
                pyeong_str = f"{pyeong_float:.1f}평"
            except Exception:
                pyeong_str = f"{pyeong_val}평"
                
            p_val = float(row.get('price_total', 0))
            p_eon = round(p_val / 10000.0, 2)
            
            pp_val = float(row.get('pyeong_price', 0))
            
            # 경과연수 및 노후도 구분 산출 (보조설명, 사용승인일자, 건축년도 연동)
            raw_age_text = row.get('보조설명', row.get('사용승인일자', row.get('건축년도', '')))
            age_info_dict = calculate_building_age_info(raw_age_text if pd.notnull(raw_age_text) and str(raw_age_text).strip() else target_build_year)
            
            properties_list.append({
                "address": addr[:35] + ('...' if len(addr) > 35 else ''),
                "deal_type": str(row.get('deal_type_val', '매매')),
                "floor_cat": row.get('floor_cat', floor_val),
                "floor_display": floor_display,
                "pyeong": pyeong_str,
                "price_total": p_val,
                "price_eon": p_eon,
                "pyeong_price": round(pp_val, 1),
                "distance": int(row.get('distance', 0)),
                "build_year": age_info_dict["year"],
                "age_years": age_info_dict["age_years"],
                "age_category": age_info_dict["category_label"],
                "age_display": age_info_dict["display"],
                "age_badge_color": age_info_dict["badge_color"],
                "zoning_label": str(row.get("zoning_label", "") or "")
            })

    target_age_info = calculate_building_age_info(target_build_year)

    sale_count = len(sale_matched) if 'sale_matched' in locals() else 0
    rent_count = len(jeonse_matched) if 'jeonse_matched' in locals() else 0

    type_label_str = "토지" if is_land else ("오피스텔" if is_officetel else ("주택" if is_housing else "상가/근린"))
    floor_display_cat = "지하" if str(target_floor_cat).startswith("B") else target_floor_cat
    area_display_cat = format_area_category_label(target_area_cat, is_commercial=is_commercial)

    # 탐색 범위(반경 또는 상업지역) 내 그룹별(층수 / 건축년도 / 평수 소·중·대 / 복합) 평당가·전월세·환산전세가율 비교 산출
    group_comparison = {"by_floor": [], "by_age": [], "by_area": [], "matrix_3d": []}
    try:
        scope_df = df[df['distance'] <= radius_used].copy()
        if len(scope_df) > 0 and not is_land:
            fc_s = scope_df['floor_cat'].astype(str)
            scope_df['_fg'] = np.where(fc_s.str.startswith('B'), '지하', fc_s)
            scope_df['_ag'] = np.select(
                [scope_df['age_cat'] == 10, scope_df['age_cat'] == 25],
                ['10년 이내', '25년 이내'],
                default='25년 이상'
            )
            if is_commercial:
                scope_df['_arg'] = np.select(
                    [scope_df['area_cat'] == 15, scope_df['area_cat'] == 30],
                    ['소 (15평 이하)', '중 (30평 이하)'],
                    default='대 (30평 이상)'
                )
                floor_order = ['1층', '지하', '저', '중', '고']
                area_order = ['소 (15평 이하)', '중 (30평 이하)', '대 (30평 이상)']
            else:
                scope_df['_arg'] = scope_df['area_cat'].astype(str) + '평대'
                floor_order = ['저', '중', '고', '지하']
                area_order = ['10평대', '20평대', '30평대', '40평대']
            age_order = ['10년 이내', '25년 이내', '25년 이상']

            dt_s = scope_df['deal_type_val'].fillna('').astype(str)
            rv_s = pd.to_numeric(scope_df.get('rent_val', 0), errors='coerce').fillna(0.0)
            is_r_mask = (rv_s > 0) | dt_s.str.contains('전세|월세|단기임대', na=False)
            is_s_mask = dt_s.str.contains('매매', na=False) & (~is_r_mask)
            scope_df['_is_s'] = is_s_mask
            scope_df['_is_r'] = is_r_mask
            scope_df['_rv'] = rv_s
            scope_df['_dep'] = np.where(is_r_mask, np.maximum(0.0, scope_df['price_total'] - rv_s * 100.0), scope_df['price_total'])

            def _summarize_grp(sub):
                s_rows = sub[sub['_is_s']]
                r_rows = sub[sub['_is_r']]
                sc = int(len(s_rows))
                rc = int(len(r_rows))
                s_pp = float(s_rows['pyeong_price'].dropna().mean()) if sc > 0 else 0.0
                r_pp = float(r_rows['pyeong_price'].dropna().mean()) if rc > 0 else 0.0
                dep_m = float(r_rows['_dep'].mean()) if rc > 0 else 0.0
                mon_m = float(r_rows['_rv'].mean()) if rc > 0 else 0.0
                conv_m = float(r_rows['price_total'].mean()) if rc > 0 else 0.0
                jr_ask = round((r_pp / s_pp) * 100.0, 1) if (s_pp > 0 and r_pp > 0) else 0.0
                jr_90 = round((r_pp / (s_pp * 0.9)) * 100.0, 1) if (s_pp > 0 and r_pp > 0) else 0.0
                return {
                    "sale_count": sc,
                    "avg_sale_pp": round(s_pp, 1),
                    "rent_count": rc,
                    "avg_deposit_man": round(dep_m, 0),
                    "avg_rent_man": round(mon_m, 1),
                    "avg_conv_deposit_man": round(conv_m, 0),
                    "avg_conv_pp": round(r_pp, 1),
                    "jeonse_ratio_asking": jr_ask,
                    "jeonse_ratio_est90": jr_90,
                }

            for fg in floor_order:
                st = _summarize_grp(scope_df[scope_df['_fg'] == fg])
                group_comparison["by_floor"].append({"group": fg, **st})
            for ag in age_order:
                st = _summarize_grp(scope_df[scope_df['_ag'] == ag])
                group_comparison["by_age"].append({"group": ag, **st})
            for arg in area_order:
                st = _summarize_grp(scope_df[scope_df['_arg'] == arg])
                group_comparison["by_area"].append({"group": arg, **st})
            for fg in floor_order:
                for ag in age_order:
                    for arg in area_order:
                        sub_m = scope_df[(scope_df['_fg'] == fg) & (scope_df['_ag'] == ag) & (scope_df['_arg'] == arg)]
                        if len(sub_m) == 0:
                            continue
                        st = _summarize_grp(sub_m)
                        if st["sale_count"] == 0 and st["rent_count"] == 0:
                            continue
                        group_comparison["matrix_3d"].append({
                            "floor_group": fg,
                            "age_group": ag,
                            "area_group": arg,
                            **st,
                        })
    except Exception as gce:
        print(f"Group comparison build warning: {gce}")

    return {
        "radius_used": radius_used,
        "matched_count": sale_count,
        "sale_count": sale_count,
        "rent_count": rent_count,
        "is_commercial": is_commercial,
        "commercial_zone_only": bool(commercial_zone_only or single_zone_geojson),
        "commercial_zone_note": commercial_zone_note,
        "special_rule_applied": special_rule_applied,
        "special_rule_msg": special_rule_msg,
        "target_categories": {
            "type_label": type_label_str,
            "floor": floor_display_cat,
            "area": area_display_cat,
            "age": "토지 (노후도 제외)" if is_land else target_age_info["display"],
            "age_label": "토지" if is_land else target_age_info["category_label"]
        },
        "target_info": {
            "area_pyeong": round(target_area_pyeong, 1),
            "build_year": target_age_info["year"],
            "age_years": target_age_info["age_years"],
            "age_category": target_age_info["category_label"],
            "age_display": target_age_info["display"],
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
            "jeonse_ratio": round(jeonse_ratio, 1),
            "sale_count": sale_count,
            "rent_count": rent_count
        },
        "group_comparison": group_comparison,
        "properties": properties_list
    }
