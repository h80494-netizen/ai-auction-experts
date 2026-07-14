import os
import sqlite3
import pandas as pd
import numpy as np
import traceback

# 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data', '실거래가')
DB_PATH = os.path.join(BASE_DIR, 'backend', 'data', 'map_data.db')

def calculate_change_rate(df_old, df_new):
    """
    6월과 7월 데이터를 병합하여 평당가격 평균 또는 환산전세가 평균 기준 증감율을 계산합니다.
    """
    if df_old is None or df_new is None or df_old.empty or df_new.empty:
        return pd.DataFrame()
        
    for df in [df_old, df_new]:
        df.columns = df.columns.str.strip()
        df['읍면동'] = df['읍면동'].astype(str).str.strip()
        df['시군구명'] = df['시군구명'].astype(str).str.strip()
        df['시도'] = df['시도'].astype(str).str.strip()
        df['시트용_유형'] = df['시트용_유형'].astype(str).str.strip()

    merged = pd.merge(
        df_new, df_old, 
        on=['시도', '시군구명', '읍면동', '시트용_유형'],
        suffixes=('_new', '_old')
    )
    
    col_name = '평당가격_평균'
    for col in merged.columns:
        if ('환산전세가' in col or '환산' in col) and col.endswith('_new'):
            col_name = col.replace('_new', '')
            break
            
    merged['change_rate'] = ((merged[f'{col_name}_new'] - merged[f'{col_name}_old']) / merged[f'{col_name}_old']) * 100
    merged['change_rate'] = merged['change_rate'].replace([np.inf, -np.inf], np.nan)
    return merged.dropna(subset=['change_rate'])

def map_dong_to_grids(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT lat_idx, lng_idx, lat, lng FROM realprice_grids GROUP BY lat_idx, lng_idx")
    grids = cursor.fetchall()
    dong_map = {}
    
    cursor.execute("SELECT address, lat, lng FROM auctions WHERE lat IS NOT NULL AND lng IS NOT NULL")
    for addr, lat, lng in cursor.fetchall():
        if not addr: continue
        parts = addr.split()
        if len(parts) >= 3:
            sgg_name = parts[1]
            dong_name = ""
            for p in parts[2:]:
                if p.endswith(('동', '읍', '면')):
                    dong_name = p
                    break
            
            if dong_name:
                key = f"{sgg_name} {dong_name}"
                if key not in dong_map:
                    dong_map[key] = []
                
                lat_idx = int(lat / 0.00225)
                lng_idx = int(lng / 0.0028)
                dong_map[key].append((lat_idx, lng_idx))
    
    for k in dong_map:
        dong_map[k] = list(set(dong_map[k]))
        
    return dong_map

def update_db(conn, df_sales, df_rent, dong_map):
    cursor = conn.cursor()
    
    sales_updates = 0
    if not df_sales.empty:
        for idx, row in df_sales.iterrows():
            sgg = row['시군구명']
            dong = row['읍면동']
            prop_type = row['시트용_유형']
            rate = row['change_rate']
            
            if '연립다세대' in prop_type: prop_type = '다세대'
            elif '단독다가구' in prop_type: prop_type = '단독'
            
            key = f"{sgg} {dong}"
            if key in dong_map:
                for (lat_idx, lng_idx) in dong_map[key]:
                    cursor.execute('''
                        UPDATE realprice_grids 
                        SET sale_price_change_rate = ?
                        WHERE lat_idx = ? AND lng_idx = ? AND property_type = ?
                    ''', (rate, lat_idx, lng_idx, prop_type))
                    sales_updates += cursor.rowcount

    rent_updates = 0
    if not df_rent.empty:
        for idx, row in df_rent.iterrows():
            sgg = row['시군구명']
            dong = row['읍면동']
            prop_type = row['시트용_유형']
            rate = row['change_rate']
            
            if '연립다세대' in prop_type: prop_type = '다세대'
            elif '단독다가구' in prop_type: prop_type = '단독'
            
            key = f"{sgg} {dong}"
            if key in dong_map:
                for (lat_idx, lng_idx) in dong_map[key]:
                    cursor.execute('''
                        UPDATE realprice_grids 
                        SET rent_price_change_rate = ?
                        WHERE lat_idx = ? AND lng_idx = ? AND property_type = ?
                    ''', (rate, lat_idx, lng_idx, prop_type))
                    rent_updates += cursor.rowcount
                
    conn.commit()
    print(f"매매 업데이트 건수: {sales_updates}")
    print(f"전월세 업데이트 건수: {rent_updates}")

def safe_read_excel(filepath):
    try:
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return None
        return pd.read_excel(filepath)
    except Exception as e:
        print(f"Failed to read {filepath}: {e}")
        return None

def get_latest_two_files(prefix):
    import glob
    files = glob.glob(os.path.join(DATA_DIR, f'{prefix}*.xlsx'))
    # 파일명에 날짜가 포함되어 있으므로 알파벳순 정렬하면 시간순 정렬됨
    files.sort(reverse=True)
    
    if len(files) < 2:
        print(f"{prefix} 파일이 2개 이상 필요합니다. (현재 {len(files)}개)")
        return None, None
        
    return files[1], files[0] # old_file, new_file

def main():
    print("데이터 분석 시작 (전월 대비 증감율 자동 계산)...")
    
    file_sales_old, file_sales_new = get_latest_two_files('부동산_실거래가_매매_분석_')
    file_rent_old, file_rent_new = get_latest_two_files('부동산_실거래가_전월세_분석_')
    
    if file_sales_old and file_sales_new:
        print(f"매매 기준월(이전): {os.path.basename(file_sales_old)}")
        print(f"매매 비교월(최신): {os.path.basename(file_sales_new)}")
        df_sales_old = safe_read_excel(file_sales_old)
        df_sales_new = safe_read_excel(file_sales_new)
        df_sales_rate = calculate_change_rate(df_sales_old, df_sales_new)
    else:
        df_sales_rate = pd.DataFrame()
        
    if file_rent_old and file_rent_new:
        print(f"전월세 기준월(이전): {os.path.basename(file_rent_old)}")
        print(f"전월세 비교월(최신): {os.path.basename(file_rent_new)}")
        df_rent_old = safe_read_excel(file_rent_old)
        df_rent_new = safe_read_excel(file_rent_new)
        df_rent_rate = calculate_change_rate(df_rent_old, df_rent_new)
    else:
        df_rent_rate = pd.DataFrame()
    
    print(f"계산된 매매 증감율 건수: {len(df_sales_rate)}")
    print(f"계산된 전월세 증감율 건수: {len(df_rent_rate)}")
    
    conn = sqlite3.connect(DB_PATH)
    dong_map = map_dong_to_grids(conn)
    print(f"동 -> 그리드 매핑 완료 (총 {len(dong_map)}개 동)")
    
    update_db(conn, df_sales_rate, df_rent_rate, dong_map)
    conn.close()
    
    print("완료되었습니다.")

if __name__ == '__main__':
    main()
