import os
import glob
import sqlite3
import pandas as pd
import numpy as np
import requests
import json
import re
import sys
import time

# Ensure output is printed in utf-8
if sys.stdout.encoding != 'utf-8':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'map_data.db')
REALPRICE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'realprice')
KAKAO_API_KEY = "9e5265220f87e54e4379077cb60071bb"

# Grid size definitions (approx. 250m)
LAT_STEP = 0.00225
LNG_STEP = 0.0028

def init_db(conn):
    cursor = conn.cursor()
    # Create the grid summary table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS realprice_grids (
            lat_idx INTEGER,
            lng_idx INTEGER,
            property_type TEXT,
            lat REAL,
            lng REAL,
            avg_price_per_pyeong REAL,
            avg_deposit_per_pyeong REAL,
            avg_rent REAL,
            jeonse_ratio REAL,
            transaction_count INTEGER,
            sale_count INTEGER,
            rent_count INTEGER,
            age_premium_ratio REAL,
            floor_sensitivity REAL,
            sales_count_under_10 INTEGER,
            sales_count_10_to_20 INTEGER,
            sales_count_20_to_30 INTEGER,
            sales_count_over_30 INTEGER,
            PRIMARY KEY (lat_idx, lng_idx, property_type)
        )
    ''')
    
    # Create an address geocode cache table to avoid repeated API calls
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS realprice_addr_cache (
            address TEXT PRIMARY KEY,
            lat REAL,
            lng REAL
        )
    ''')
    conn.commit()

def build_dong_coords_map(conn):
    """
    Builds a fallback database of legal dong center coordinates using the existing auctions table
    and other spatial POIs in the database.
    """
    print("Building legal dong coordinates dictionary from existing DB data...")
    cursor = conn.cursor()
    dong_map = {}
    
    # Query auctions table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auctions'")
    if cursor.fetchone():
        cursor.execute("SELECT address, lat, lng FROM auctions WHERE lat IS NOT NULL AND lng IS NOT NULL")
        rows = cursor.fetchall()
        for addr, lat, lng in rows:
            if not addr: continue
            # Extract legal dong (usually ending with 동, 읍, 면)
            match = re.search(r'([가-힣\d]+(?:동|읍|면))', addr)
            if match:
                dong = match.group(1)
                # Parse city/gu for uniqueness (e.g. "성남시 금광동")
                match_sgg = re.search(r'([가-힣]+시\s+[가-힣]+구|[가-힣]+시|[가-힣]+군)', addr)
                sgg = match_sgg.group(1) if match_sgg else ""
                key = f"{sgg} {dong}".strip()
                if key not in dong_map:
                    dong_map[key] = []
                dong_map[key].append((lat, lng))

    # Calculate average coordinate for each dong
    dong_centers = {}
    for dong, coords in dong_map.items():
        lats = [c[0] for c in coords]
        lngs = [c[1] for c in coords]
        dong_centers[dong] = (sum(lats) / len(lats), sum(lngs) / len(lngs))
        
    print(f"Created center coordinates for {len(dong_centers)} dongs.")
    return dong_centers

def build_local_geocode_map(conn):
    print("Building local geocoding dictionary from auctions and other tables...")
    cursor = conn.cursor()
    local_map = {}
    
    # 1. Load from auctions
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auctions'")
    if cursor.fetchone():
        cursor.execute("SELECT address, lat, lng FROM auctions WHERE lat IS NOT NULL AND lng IS NOT NULL")
        for addr, lat, lng in cursor.fetchall():
            if not addr: continue
            local_map[addr.strip()] = (lat, lng)
            
            # Also build sub-keys like "시군구 번지" or "시군구 건물명"
            # Split address: 경기도 성남시 중원구 금광동 123-4
            parts = addr.split()
            if len(parts) >= 3:
                dong_idx = -1
                for i, p in enumerate(parts):
                    if p.endswith(('동', '읍', '면')):
                        dong_idx = i
                        break
                if dong_idx != -1:
                    sgg = " ".join(parts[:dong_idx+1])
                    rest = " ".join(parts[dong_idx+1:])
                    # Remove brackets
                    rest_clean = rest.split('[')[0].split('(')[0].strip()
                    key = f"{sgg} {rest_clean}".strip()
                    if key:
                        local_map[key] = (lat, lng)
                        
    # 2. Load from bus_stops
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bus_stops'")
    if cursor.fetchone():
        cursor.execute("SELECT address, lat, lng FROM bus_stops WHERE lat IS NOT NULL AND lng IS NOT NULL")
        for addr, lat, lng in cursor.fetchall():
            if addr:
                local_map[addr.strip()] = (lat, lng)
                
    print(f"Created local geocode dictionary with {len(local_map)} entries.")
    return local_map

def get_coordinate_via_kakao(address):
    """
    Geocodes an address via Kakao Search API
    """
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": address}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data.get("documents") and len(data["documents"]) > 0:
                doc = data["documents"][0]
                return float(doc["y"]), float(doc["x"])
    except Exception as e:
        print(f"Kakao API error for {address}: {e}")
    return None, None

def load_address_cache(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT address, lat, lng FROM realprice_addr_cache")
    return {row[0]: (row[1], row[2]) for row in cursor.fetchall()}

def save_address_cache(conn, cache):
    cursor = conn.cursor()
    for addr, (lat, lng) in cache.items():
        cursor.execute("INSERT OR REPLACE INTO realprice_addr_cache (address, lat, lng) VALUES (?, ?, ?)", (addr, lat, lng))
    conn.commit()

def parse_property_type(filename):
    """
    Extracts property type and deal type from filename.
    e.g., MOLIT_경기도_아파트_매매_1780926287.csv -> 아파트, 매매
    """
    name = os.path.basename(filename)
    types = ['아파트', '연립다세대', '오피스텔', '단독다가구', '토지', '상업업무용', '공장창고등', '분양권']
    prop_type = '기타'
    for t in types:
        if t in name:
            prop_type = t
            break
            
    # Normalize naming to match user requests
    if prop_type == '연립다세대':
        prop_type = '다세대'
    elif prop_type == '단독다가구':
        prop_type = '단독'
        
    deal_type = '매매'
    if '전월세' in name:
        deal_type = '전월세'
        
    return prop_type, deal_type

def process_csv(file_path, conn, dong_centers, addr_cache, local_map):
    prop_type, deal_type = parse_property_type(file_path)
    print(f"\nProcessing [{prop_type} | {deal_type}] File: {os.path.basename(file_path)}")
    
    try:
        # Load CSV starting from line 16 (skip first 15 lines of instructions)
        df = pd.read_csv(file_path, skiprows=15, encoding='cp949', low_memory=False)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return
        
    # Strip column names and values
    df.columns = [c.strip() for c in df.columns]
    
    # Ensure necessary columns exist
    if '시군구' not in df.columns:
        print(f"Skipping {file_path} - '시군구' column not found.")
        return
        
    transactions = []
    kakao_calls = 0
    new_cache_entries = {}
    
    # Process rows
    total_rows = len(df)
    print(f"Total rows to process: {total_rows}")
    
    # Sample 5000 rows at max per file to prevent running out of API quotas
    # and to ensure fast execution, while still maintaining highly accurate spatial indicators.
    # We prioritize latest deals
    if '계약년월' in df.columns:
        df = df.sort_values(by=['계약년월'], ascending=False)
        
    sample_size = min(5000, total_rows)
    df_sample = df.head(sample_size)
    
    for idx, row in df_sample.iterrows():
        sgg = str(row.get('시군구', '')).strip()
        if not sgg or sgg == 'nan': continue
        
        # Build address
        dong_match = re.search(r'([가-힣\d]+(?:동|읍|면))', sgg)
        dong = dong_match.group(1) if dong_match else ""
        
        # Unique dong key (e.g., "성남시 중원구 금광동")
        match_sgg = re.search(r'([가-힣]+시\s+[가-힣]+구|[가-힣]+시|[가-힣]+군)', sgg)
        sgg_name = match_sgg.group(1) if match_sgg else ""
        dong_key = f"{sgg_name} {dong}".strip()
        
        # Retrieve coordinates
        lat, lng = None, None
        
        # 1. Try to search in Kakao cache or Kakao API if exact address details exist
        bonbun = str(row.get('번지', row.get('지번', ''))).strip()
        name_col = str(row.get('단지명', row.get('건물명', row.get('도로명', '')))).strip()
        
        # Use exact address if it doesn't contain mask '***'
        exact_addr = ""
        if bonbun and '*' not in bonbun and bonbun != 'nan':
            exact_addr = f"{sgg} {bonbun}"
        elif name_col and name_col != 'nan':
            exact_addr = f"{sgg} {name_col}"
            
        if exact_addr:
            exact_addr_clean = exact_addr.strip()
            if exact_addr_clean in local_map:
                lat, lng = local_map[exact_addr_clean]
            elif exact_addr in addr_cache:
                lat, lng = addr_cache[exact_addr]
            elif exact_addr in new_cache_entries:
                lat, lng = new_cache_entries[exact_addr]
            elif kakao_calls < 5:  # Cap Kakao API calls per file to prevent lockups
                lat, lng = get_coordinate_via_kakao(exact_addr)
                kakao_calls += 1
                if lat and lng:
                    new_cache_entries[exact_addr] = (lat, lng)
                time.sleep(0.05) # Rate limit
                
        # 2. Fallback to Dong Center coords
        if not lat or not lng:
            if dong_key in dong_centers:
                lat, lng = dong_centers[dong_key]
            else:
                # Fallback to city/sgg centers if possible
                continue
                
        # Calculate grid indexing
        lat_idx = int(lat / LAT_STEP)
        lng_idx = int(lng / LNG_STEP)
        
        # Parse Price
        price = 0.0
        deposit = 0.0
        rent = 0.0
        
        # Extract area size robustly
        area = 0.0
        for col in [
            '전용면적(㎡)', '전용/연면적(㎡)', '연면적(㎡)', '건물면적(㎡)', '계약면적(㎡)', '대지면적(㎡)',
            '전용면적', '연면적', '건물면적', '계약면적', '대지면적', '면적', '면적(㎡)'
        ]:
            if col in row.index:
                val = row[col]
                if pd.notna(val):
                    try:
                        area = float(str(val).replace(',', ''))
                        if area > 0:
                            break
                    except ValueError:
                        pass
                        
        if area <= 0:
            continue
        pyeong = area / 3.30578
        
        if deal_type == '매매':
            price_col = row.get('거래금액(만원)', row.get('거래금액', 0))
            try:
                price = float(str(price_col).replace(',', ''))
            except Exception:
                continue
        else: # 전월세
            dep_col = row.get('보증금(만원)', row.get('보증금', 0))
            rent_col = row.get('월세금(만원)', row.get('월세금', row.get('월세(만원)', row.get('월세', 0))))
            try:
                deposit = float(str(dep_col).replace(',', ''))
                rent = float(str(rent_col).replace(',', ''))
            except Exception:
                continue
                
        # Building Age
        build_year = 0
        year_col = row.get('건축년도', 0)
        try:
            build_year = int(float(str(year_col)))
        except Exception:
            pass
            
        # Floor level
        floor = 0
        floor_col = row.get('층', '')
        try:
            if floor_col and str(floor_col).isdigit():
                floor = int(floor_col)
        except Exception:
            pass
            
        transactions.append({
            'lat_idx': lat_idx,
            'lng_idx': lng_idx,
            'lat': lat,
            'lng': lng,
            'price': price,
            'deposit': deposit,
            'rent': rent,
            'pyeong': pyeong,
            'build_year': build_year,
            'floor': floor
        })
        
    # Save newly resolved Kakao addresses
    if new_cache_entries:
        addr_cache.update(new_cache_entries)
        save_address_cache(conn, new_cache_entries)
        
    if not transactions:
        print("No valid transactions parsed from this file.")
        return
        
    # Aggregate by Grid (lat_idx, lng_idx)
    df_trans = pd.DataFrame(transactions)
    
    # Calculate price per pyeong
    df_trans['price_per_pyeong'] = np.where(df_trans['price'] > 0, df_trans['price'] / df_trans['pyeong'], np.nan)
    # Calculate converted deposit (보증금 + 월세 * 100)
    df_trans['converted_deposit'] = df_trans['deposit'] + df_trans['rent'] * 100
    df_trans['deposit_per_pyeong'] = np.where(df_trans['converted_deposit'] > 0, df_trans['converted_deposit'] / df_trans['pyeong'], np.nan)
    
    grouped = df_trans.groupby(['lat_idx', 'lng_idx'])
    
    cursor = conn.cursor()
    grid_inserts = 0
    
    current_year = 2026 # Context standard
    
    for (lat_idx, lng_idx), group in grouped:
        lat_idx = int(lat_idx)
        lng_idx = int(lng_idx)
        # Basic aggregates
        avg_lat = group['lat'].mean()
        avg_lng = group['lng'].mean()
        
        prices = group['price_per_pyeong'].dropna()
        # Use median for price
        avg_price = prices.median() if len(prices) > 0 else 0.0
        if np.isnan(avg_price): avg_price = 0.0
        
        # Pyeong size counts (specifically for sale transactions)
        sales_count_under_10 = 0
        sales_count_10_to_20 = 0
        sales_count_20_to_30 = 0
        sales_count_over_30 = 0
        
        if deal_type == '매매':
            sale_count = len(group)
            rent_count = 0
            sales_count_under_10 = len(group[group['pyeong'] <= 10])
            sales_count_10_to_20 = len(group[(group['pyeong'] > 10) & (group['pyeong'] <= 20)])
            sales_count_20_to_30 = len(group[(group['pyeong'] > 20) & (group['pyeong'] <= 30)])
            sales_count_over_30 = len(group[group['pyeong'] > 30])
        else:
            sale_count = 0
            rent_count = len(group)
        
        deposits = group['deposit_per_pyeong'].dropna()
        # Use median for converted deposit
        avg_deposit = deposits.median() if len(deposits) > 0 else 0.0
        if np.isnan(avg_deposit): avg_deposit = 0.0
        
        rents = group[group['rent'] > 0]['rent']
        # Use median for rent
        avg_rent = rents.median() if len(rents) > 0 else 0.0
        if np.isnan(avg_rent): avg_rent = 0.0
        
        # Calculate Jeonse Ratio (%)
        jeonse_ratio = 0.0
        if avg_price > 0 and avg_deposit > 0:
            jeonse_ratio = (avg_deposit / avg_price) * 100
            
        # Age Premium: New build (<= 5 years) vs Old build (>= 20 years)
        age_premium = 0.0
        if 'build_year' in group.columns and (group['build_year'] > 0).any():
            group_build = group[group['build_year'] > 0].copy()
            group_build['age'] = current_year - group_build['build_year']
            
            new_builds = group_build[group_build['age'] <= 5]
            old_builds = group_build[group_build['age'] >= 20]
            
            if len(new_builds) > 0 and len(old_builds) > 0:
                new_avg = new_builds['price_per_pyeong'].median() # median for age premium
                old_avg = old_builds['price_per_pyeong'].median() # median for age premium
                if old_avg > 0 and not np.isnan(new_avg) and not np.isnan(old_avg):
                    age_premium = new_avg / old_avg
                    
        # Floor Sensitivity: Low floors (1-3) vs High/Royal floors (>= 10)
        floor_sensitivity = 0.0
        if 'floor' in group.columns and (group['floor'] > 0).any():
            group_floor = group[group['floor'] > 0]
            low_floors = group_floor[group_floor['floor'] <= 3]
            high_floors = group_floor[group_floor['floor'] >= 10]
            
            if len(low_floors) > 0 and len(high_floors) > 0:
                low_avg = low_floors['price_per_pyeong'].median() # median for floor sensitivity
                high_avg = high_floors['price_per_pyeong'].median() # median for floor sensitivity
                if low_avg > 0 and not np.isnan(low_avg) and not np.isnan(high_avg):
                    # Ratio of royal floor price relative to low floor price (typically > 1.0)
                    floor_sensitivity = high_avg / low_avg
        
        # Load existing data to merge deal types
        cursor.execute('''
            SELECT avg_price_per_pyeong, avg_deposit_per_pyeong, avg_rent, 
                   jeonse_ratio, transaction_count, sale_count, rent_count, 
                   age_premium_ratio, floor_sensitivity,
                   sales_count_under_10, sales_count_10_to_20, sales_count_20_to_30, sales_count_over_30
            FROM realprice_grids 
            WHERE lat_idx = ? AND lng_idx = ? AND property_type = ?
        ''', (lat_idx, lng_idx, prop_type))
        
        existing = cursor.fetchone()
        if existing:
            # Merge logic
            (ex_avg_price, ex_avg_deposit, ex_avg_rent, ex_jeonse, ex_count, ex_sale_count, ex_rent_count, ex_age, ex_floor,
             ex_sales_under_10, ex_sales_10s, ex_sales_20s, ex_sales_over_30) = existing
            
            if deal_type == '매매':
                final_avg_price = avg_price
                final_avg_deposit = ex_avg_deposit
                final_avg_rent = ex_avg_rent
                final_sale_count = sale_count
                final_rent_count = ex_rent_count
                final_sales_under_10 = sales_count_under_10
                final_sales_10s = sales_count_10_to_20
                final_sales_20s = sales_count_20_to_30
                final_sales_over_30 = sales_count_over_30
                final_age = age_premium if age_premium > 0 else ex_age
                final_floor = floor_sensitivity if floor_sensitivity > 0 else ex_floor
            else: # 전월세
                final_avg_price = ex_avg_price
                final_avg_deposit = avg_deposit
                final_avg_rent = avg_rent
                final_sale_count = ex_sale_count
                final_rent_count = rent_count
                final_sales_under_10 = ex_sales_under_10
                final_sales_10s = ex_sales_10s
                final_sales_20s = ex_sales_20s
                final_sales_over_30 = ex_sales_over_30
                final_age = ex_age
                final_floor = ex_floor
                
            # Recompute Jeonse Ratio
            final_jeonse = ex_jeonse
            if final_avg_price > 0 and final_avg_deposit > 0:
                final_jeonse = (final_avg_deposit / final_avg_price) * 100
        else:
            if deal_type == '매매':
                final_avg_price = avg_price
                final_avg_deposit = 0.0
                final_avg_rent = 0.0
                final_sale_count = sale_count
                final_rent_count = 0
                final_sales_under_10 = sales_count_under_10
                final_sales_10s = sales_count_10_to_20
                final_sales_20s = sales_count_20_to_30
                final_sales_over_30 = sales_count_over_30
                final_jeonse = 0.0
            else: # 전월세
                final_avg_price = 0.0
                final_avg_deposit = avg_deposit
                final_avg_rent = avg_rent
                final_sale_count = 0
                final_rent_count = rent_count
                final_sales_under_10 = 0
                final_sales_10s = 0
                final_sales_20s = 0
                final_sales_over_30 = 0
                final_jeonse = 0.0
                
            final_age = age_premium
            final_floor = floor_sensitivity
            
        final_count = final_sale_count + final_rent_count
            
        cursor.execute('''
            INSERT OR REPLACE INTO realprice_grids (
                lat_idx, lng_idx, property_type, lat, lng, 
                avg_price_per_pyeong, avg_deposit_per_pyeong, avg_rent, 
                jeonse_ratio, transaction_count, sale_count, rent_count, 
                age_premium_ratio, floor_sensitivity,
                sales_count_under_10, sales_count_10_to_20, sales_count_20_to_30, sales_count_over_30
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            lat_idx, lng_idx, prop_type, avg_lat, avg_lng,
            final_avg_price, final_avg_deposit, final_avg_rent,
            final_jeonse, final_count, final_sale_count, final_rent_count,
            final_age, final_floor,
            final_sales_under_10, final_sales_10s, final_sales_20s, final_sales_over_30
        ))
        grid_inserts += 1
        
    conn.commit()
    print(f"Upserted {grid_inserts} grid summaries into DB.")

def main():
    print(f"Connecting to database: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        # Fallback to backend dir in case of execution context issues
        print("Database path not found. Checking fallback...")
        
    conn = sqlite3.connect(DB_PATH)
    
    # 0. Drop existing realprice_grids table to apply new schema
    print("Dropping existing realprice_grids table for schema update...")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS realprice_grids")
    conn.commit()
    
    init_db(conn)
    
    # 1. Build Dong coordinates map
    dong_centers = build_dong_coords_map(conn)
    
    # 1.5. Build Local geocode cache from auctions
    local_map = build_local_geocode_map(conn)
    
    # 2. Load Address Geocode Cache
    addr_cache = load_address_cache(conn)
    print(f"Loaded {len(addr_cache)} geocoded addresses from cache.")
    
    # 3. Find CSV files
    csv_files = glob.glob(os.path.join(REALPRICE_DIR, "*.csv"))
    print(f"Found {len(csv_files)} CSV files in realprice directory.")
    
    # Sort files so that '매매' is processed first, setting the base prices, 
    # followed by '전월세' which will overlay deposits and calculate Jeonse ratios.
    csv_files.sort(key=lambda x: 0 if '매매' in x else 1)
    
    for f in csv_files:
        process_csv(f, conn, dong_centers, addr_cache, local_map)
        
    conn.close()
    print("\nReal price data migration and grid aggregation completed successfully!")

if __name__ == "__main__":
    main()
