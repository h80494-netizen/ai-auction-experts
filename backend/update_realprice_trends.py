import os
import sys
import sqlite3
import pandas as pd
import numpy as np
import traceback
import glob
import requests
import re
from python_calamine import CalamineWorkbook

# 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data', '실거래가')
DB_PATH = os.path.join(BASE_DIR, 'backend', 'data', 'map_data.db')
KAKAO_API_KEY = "9e5265220f87e54e4379077cb60071bb"

LAT_STEP = 0.00225
LNG_STEP = 0.0028

def geocode_address(address):
    """카카오 로컬 API를 통해 주소 좌표를 조회합니다."""
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": address}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=4)
        if res.status_code == 200:
            docs = res.json().get("documents", [])
            if docs:
                return float(docs[0]["y"]), float(docs[0]["x"])
    except Exception:
        pass
    return None, None

def load_excel_robust(filepath, deal_type='매매'):
    """
    실거래가 분석 엑셀 파일을 로드합니다.
    - 종합 시트에 유효 데이터가 있는 경우 종합 시트를 우선 로드합니다.
    - 각 개별 시트의 유효 데이터를 함께 모아 동별/유형별 평균, 중앙값, 거래건수를 집계합니다.
    """
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return pd.DataFrame()
        
    print(f"Loading {deal_type} data from {os.path.basename(filepath)}...")
    
    try:
        df_summary = pd.read_excel(filepath, sheet_name=0)
        df_summary.columns = [c.strip() for c in df_summary.columns]
        valid_summary = df_summary.dropna(subset=['시군구명', '읍면동', '시트용_유형'])
        if len(valid_summary) > 50:
            print(f"  Loaded {len(valid_summary)} valid rows directly from summary sheet.")
            return valid_summary
    except Exception as e:
        print(f"  Summary sheet quick read warning: {e}")

    try:
        wb = CalamineWorkbook.from_path(filepath)
        summary_rows = []
        detail_rows = []
        for sname in wb.sheet_names:
            sheet = wb.get_sheet_by_name(sname)
            data = sheet.to_python()
            if not data or len(data) < 2:
                continue
            header = [str(h).strip() if h is not None else '' for h in data[0]]
            
            if sname in ['종합매매', '종합전월세']:
                for r in data[1:]:
                    if len(r) >= 4 and r[1] and r[2] and r[3]:
                        row_dict = {header[i]: r[i] for i in range(min(len(header), len(r)))}
                        summary_rows.append(row_dict)
                continue
                
            prop_type = sname.replace('매매_1', '').replace('매매_2', '').replace('매매', '')
            prop_type = prop_type.replace('전월세_1', '').replace('전월세_2', '').replace('전월세_3', '').replace('전월세', '')
            if '연립다세대' in prop_type: prop_type = '다세대'
            elif '단독다가구' in prop_type: prop_type = '단독'
            
            for r in data[1:]:
                if len(r) >= 3 and r[1] and str(r[1]).strip() and r[2] and str(r[2]).strip():
                    row_dict = {header[i]: r[i] for i in range(min(len(header), len(r)))}
                    row_dict['시트용_유형'] = prop_type
                    
                    price_col = '평당가격(만원)' if '평당가격(만원)' in row_dict else '평당가격'
                    val = row_dict.get(price_col)
                    if val is not None and str(val).strip() != '':
                        try:
                            row_dict['price_numeric'] = float(str(val).replace(',', ''))
                        except Exception:
                            row_dict['price_numeric'] = np.nan
                    else:
                        row_dict['price_numeric'] = np.nan
                        
                    detail_rows.append(row_dict)
                    
        frames = []
        if summary_rows:
            df_sum = pd.DataFrame(summary_rows)
            df_sum.columns = [c.strip() for c in df_sum.columns]
            frames.append(df_sum)
            
        if detail_rows:
            df_det = pd.DataFrame(detail_rows)
            df_det.columns = [c.strip() for c in df_det.columns]
            grouped = df_det.groupby(['시도', '시군구명', '읍면동', '시트용_유형'])
            agg_col_mean = '환산평당가_평균' if deal_type == '전월세' else '평당가격_평균'
            agg_col_med = '환산평당가_중앙값' if deal_type == '전월세' else '평당가격_중앙값'
            
            agg_df = grouped.agg(
                mean_val=('price_numeric', 'mean'),
                med_val=('price_numeric', 'median'),
                cnt=('price_numeric', 'count')
            ).reset_index()
            
            agg_df.rename(columns={
                'mean_val': agg_col_mean,
                'med_val': agg_col_med,
                'cnt': '거래건수'
            }, inplace=True)
            frames.append(agg_df)
            
        if frames:
            combined = pd.concat(frames, ignore_index=True)
            combined = combined.drop_duplicates(subset=['시도', '시군구명', '읍면동', '시트용_유형'], keep='last')
            print(f"  Extracted and aggregated {len(combined)} distinct dong/property_type records.")
            return combined
    except Exception as e:
        print(f"  Error parsing sheets: {e}")
        traceback.print_exc()

    return pd.DataFrame()

def calculate_change_rate(df_old, df_new):
    """
    이전(8월)과 최신(9월) 데이터를 병합하여 평당가격 평균 또는 환산전세가 평균 기준 증감율을 계산합니다.
    9월 데이터에 없는 8월의 기존 항목은 그대로 보존됩니다.
    """
    if df_old is None or df_old.empty:
        return pd.DataFrame()
        
    for df in [df_old, df_new]:
        if df is not None and not df.empty:
            df.columns = df.columns.str.strip()
            df['읍면동'] = df['읍면동'].astype(str).str.strip()
            df['시군구명'] = df['시군구명'].astype(str).str.strip()
            df['시도'] = df['시도'].astype(str).str.strip()
            df['시트용_유형'] = df['시트용_유형'].astype(str).str.strip()

    if df_new is None or df_new.empty:
        return pd.DataFrame()

    merged = pd.merge(
        df_new, df_old, 
        on=['시도', '시군구명', '읍면동', '시트용_유형'],
        suffixes=('_new', '_old'),
        how='inner'
    )
    
    if merged.empty:
        # Fallback: 시군구명/읍면동/유형 매칭
        print("Retrying merge by (시군구명, 읍면동, 유형)...")
        merged = pd.merge(
            df_new, df_old,
            on=['시군구명', '읍면동', '시트용_유형'],
            suffixes=('_new', '_old'),
            how='inner'
        )
        
    if merged.empty:
        print("No intersecting dong/property_type found between old and new.")
        return pd.DataFrame()
        
    col_name = '평당가격_평균'
    for col in merged.columns:
        if ('환산평당가' in col or '환산' in col) and col.endswith('_new'):
            col_name = col.replace('_new', '')
            break
            
    col_new = f'{col_name}_new'
    col_old = f'{col_name}_old'
    
    if col_new in merged.columns and col_old in merged.columns:
        merged['change_rate'] = ((pd.to_numeric(merged[col_new], errors='coerce') - pd.to_numeric(merged[col_old], errors='coerce')) / pd.to_numeric(merged[col_old], errors='coerce')) * 100
        merged['change_rate'] = merged['change_rate'].replace([np.inf, -np.inf], np.nan)
        return merged.dropna(subset=['change_rate'])
        
    return pd.DataFrame()

def map_dong_to_grids(conn):
    cursor = conn.cursor()
    dong_map = {}
    
    def add_entry(key, lat, lng):
        if not key: return
        key = key.strip()
        if key not in dong_map:
            dong_map[key] = []
        lat_idx = int(lat / LAT_STEP)
        lng_idx = int(lng / LNG_STEP)
        dong_map[key].append((lat_idx, lng_idx))

    # 1. Load from auctions
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auctions'")
    if cursor.fetchone():
        cursor.execute("SELECT address, lat, lng FROM auctions WHERE lat IS NOT NULL AND lng IS NOT NULL")
        for addr, lat, lng in cursor.fetchall():
            if not addr: continue
            parts = addr.split()
            if len(parts) >= 2:
                sgg_name = parts[1]
                dong_name = ""
                for p in parts[2:]:
                    if p.endswith(('동', '읍', '면', '리', '가')):
                        dong_name = p
                        break
                
                if dong_name:
                    add_entry(f"{sgg_name} {dong_name}", lat, lng)
                    add_entry(dong_name, lat, lng)
                    if len(parts) >= 3:
                        add_entry(f"{parts[0]} {sgg_name} {dong_name}", lat, lng)

    # 2. Load from realprice_addr_cache if available
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='realprice_addr_cache'")
    if cursor.fetchone():
        cursor.execute("SELECT address, lat, lng FROM realprice_addr_cache WHERE lat IS NOT NULL AND lng IS NOT NULL")
        for addr, lat, lng in cursor.fetchall():
            if not addr: continue
            parts = addr.split()
            if len(parts) >= 2:
                sgg_name = parts[1]
                dong_name = ""
                for p in parts[2:]:
                    if p.endswith(('동', '읍', '면', '리', '가')):
                        dong_name = p
                        break
                if dong_name:
                    add_entry(f"{sgg_name} {dong_name}", lat, lng)
                    add_entry(dong_name, lat, lng)

    # 3. Load from existing realprice_grids centers
    cursor.execute("SELECT lat_idx, lng_idx, lat, lng FROM realprice_grids GROUP BY lat_idx, lng_idx")
    
    for k in dong_map:
        dong_map[k] = list(set(dong_map[k]))
        
    return dong_map

def update_db(conn, df_sales, df_rent, dong_map):
    cursor = conn.cursor()
    
    sales_updates = 0
    if df_sales is not None and not df_sales.empty:
        for idx, row in df_sales.iterrows():
            sido = str(row.get('시도', '')).strip()
            sgg = str(row.get('시군구명', '')).strip()
            dong = str(row.get('읍면동', '')).strip()
            prop_type = str(row.get('시트용_유형', '')).strip()
            rate = row.get('change_rate')
            price_new = row.get('평당가격_평균_new', row.get('평당가격_평균'))
            
            if '연립다세대' in prop_type: prop_type = '다세대'
            elif '단독다가구' in prop_type: prop_type = '단독'
            
            keys = [f"{sido} {sgg} {dong}", f"{sgg} {dong}", dong]
            matched_grids = []
            for k in keys:
                if k in dong_map and dong_map[k]:
                    matched_grids = dong_map[k]
                    break
                    
            if not matched_grids:
                # Fallback: Geocode via Kakao
                query_addr = f"{sido} {sgg} {dong}".strip()
                lat, lng = geocode_address(query_addr)
                if lat and lng:
                    lat_idx = int(lat / LAT_STEP)
                    lng_idx = int(lng / LNG_STEP)
                    matched_grids = [(lat_idx, lng_idx)]
                    dong_map[f"{sgg} {dong}"] = matched_grids
                    
            if matched_grids:
                for (lat_idx, lng_idx) in matched_grids:
                    # Update change rate
                    cursor.execute('''
                        UPDATE realprice_grids 
                        SET sale_price_change_rate = ?
                        WHERE lat_idx = ? AND lng_idx = ? AND property_type = ?
                    ''', (rate, lat_idx, lng_idx, prop_type))
                    if cursor.rowcount > 0:
                        sales_updates += cursor.rowcount
                    else:
                        # If grid doesn't exist for this property type, insert new row
                        lat = (lat_idx + 0.5) * LAT_STEP
                        lng = (lng_idx + 0.5) * LNG_STEP
                        avg_p = float(price_new) if price_new and not np.isnan(price_new) else 0.0
                        cursor.execute('''
                            INSERT OR IGNORE INTO realprice_grids (
                                lat_idx, lng_idx, property_type, lat, lng,
                                avg_price_per_pyeong, avg_deposit_per_pyeong, avg_rent,
                                jeonse_ratio, transaction_count, sale_count, rent_count,
                                age_premium_ratio, floor_sensitivity,
                                sales_count_under_10, sales_count_10_to_20, sales_count_20_to_30, sales_count_over_30,
                                sale_price_change_rate, rent_price_change_rate
                            ) VALUES (?, ?, ?, ?, ?, ?, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, ?, NULL)
                        ''', (lat_idx, lng_idx, prop_type, lat, lng, avg_p, rate))
                        sales_updates += cursor.rowcount

    rent_updates = 0
    if df_rent is not None and not df_rent.empty:
        for idx, row in df_rent.iterrows():
            sido = str(row.get('시도', '')).strip()
            sgg = str(row.get('시군구명', '')).strip()
            dong = str(row.get('읍면동', '')).strip()
            prop_type = str(row.get('시트용_유형', '')).strip()
            rate = row.get('change_rate')
            dep_new = row.get('환산평당가_평균_new', row.get('환산평당가_평균'))
            
            if '연립다세대' in prop_type: prop_type = '다세대'
            elif '단독다가구' in prop_type: prop_type = '단독'
            
            keys = [f"{sido} {sgg} {dong}", f"{sgg} {dong}", dong]
            matched_grids = []
            for k in keys:
                if k in dong_map and dong_map[k]:
                    matched_grids = dong_map[k]
                    break
                    
            if not matched_grids:
                query_addr = f"{sido} {sgg} {dong}".strip()
                lat, lng = geocode_address(query_addr)
                if lat and lng:
                    lat_idx = int(lat / LAT_STEP)
                    lng_idx = int(lng / LNG_STEP)
                    matched_grids = [(lat_idx, lng_idx)]
                    dong_map[f"{sgg} {dong}"] = matched_grids
                    
            if matched_grids:
                for (lat_idx, lng_idx) in matched_grids:
                    cursor.execute('''
                        UPDATE realprice_grids 
                        SET rent_price_change_rate = ?
                        WHERE lat_idx = ? AND lng_idx = ? AND property_type = ?
                    ''', (rate, lat_idx, lng_idx, prop_type))
                    if cursor.rowcount > 0:
                        rent_updates += cursor.rowcount
                    else:
                        lat = (lat_idx + 0.5) * LAT_STEP
                        lng = (lng_idx + 0.5) * LNG_STEP
                        avg_dep = float(dep_new) if dep_new and not np.isnan(dep_new) else 0.0
                        cursor.execute('''
                            INSERT OR IGNORE INTO realprice_grids (
                                lat_idx, lng_idx, property_type, lat, lng,
                                avg_price_per_pyeong, avg_deposit_per_pyeong, avg_rent,
                                jeonse_ratio, transaction_count, sale_count, rent_count,
                                age_premium_ratio, floor_sensitivity,
                                sales_count_under_10, sales_count_10_to_20, sales_count_20_to_30, sales_count_over_30,
                                sale_price_change_rate, rent_price_change_rate
                            ) VALUES (?, ?, ?, ?, ?, 0, ?, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, NULL, ?)
                        ''', (lat_idx, lng_idx, prop_type, lat, lng, avg_dep, rate))
                        rent_updates += cursor.rowcount
                
    conn.commit()
    print(f"매매 업데이트 건수: {sales_updates}")
    print(f"전월세 업데이트 건수: {rent_updates}")

def get_target_files(prefix):
    """
    ~$ 임시 파일을 제외하고, 20260803 기준 파일과 20260903 최신 파일을 안전하게 반환합니다.
    """
    files = glob.glob(os.path.join(DATA_DIR, f'{prefix}*.xlsx'))
    files = [f for f in files if not os.path.basename(f).startswith('~$')]
    files.sort(reverse=True)
    
    if len(files) < 2:
        print(f"{prefix} 파일이 2개 이상 필요합니다. (현재 {len(files)}개)")
        return None, None
        
    new_file = files[0]
    
    old_file = None
    for f in files[1:]:
        if '004446' in f:
            old_file = f
            break
    if not old_file:
        old_file = files[1]
        
    return old_file, new_file

def main():
    print("=== 실거래가 격자 오버레이 최신화 (20260903 기준 증감율 및 시세 반영) ===")
    
    file_sales_old, file_sales_new = get_target_files('부동산_실거래가_매매_분석_')
    file_rent_old, file_rent_new = get_target_files('부동산_실거래가_전월세_분석_')
    
    if file_sales_old and file_sales_new:
        print(f"\n[매매] 기준 파일(20260803): {os.path.basename(file_sales_old)}")
        print(f"[매매] 최신 파일(20260903): {os.path.basename(file_sales_new)}")
        df_sales_old = load_excel_robust(file_sales_old, '매매')
        df_sales_new = load_excel_robust(file_sales_new, '매매')
        df_sales_rate = calculate_change_rate(df_sales_old, df_sales_new)
    else:
        df_sales_rate = pd.DataFrame()
        
    if file_rent_old and file_rent_new:
        print(f"\n[전월세] 기준 파일(20260803): {os.path.basename(file_rent_old)}")
        print(f"[전월세] 최신 파일(20260903): {os.path.basename(file_rent_new)}")
        df_rent_old = load_excel_robust(file_rent_old, '전월세')
        df_rent_new = load_excel_robust(file_rent_new, '전월세')
        df_rent_rate = calculate_change_rate(df_rent_old, df_rent_new)
    else:
        df_rent_rate = pd.DataFrame()
    
    print(f"\n계산된 매매 증감율 건수: {len(df_sales_rate)}")
    if not df_sales_rate.empty:
        cols_to_show = [c for c in ['시도', '시군구명', '읍면동', '시트용_유형', 'change_rate'] if c in df_sales_rate.columns]
        print(df_sales_rate[cols_to_show].head(10))
        
    print(f"\n계산된 전월세 증감율 건수: {len(df_rent_rate)}")
    if not df_rent_rate.empty:
        cols_to_show = [c for c in ['시도', '시군구명', '읍면동', '시트용_유형', 'change_rate'] if c in df_rent_rate.columns]
        print(df_rent_rate[cols_to_show].head(10))
    
    conn = sqlite3.connect(DB_PATH)
    dong_map = map_dong_to_grids(conn)
    print(f"\n동 -> 그리드 매핑 완료 (총 {len(dong_map)}개 동 매핑 사전)")
    
    update_db(conn, df_sales_rate, df_rent_rate, dong_map)
    conn.close()
    
    print("\n20260903 최신 기준 실거래가 격자 오버레이 업데이트가 성공적으로 완료되었습니다.")

if __name__ == '__main__':
    main()

