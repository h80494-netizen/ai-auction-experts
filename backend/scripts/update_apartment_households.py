import pandas as pd
import sqlite3
import os
import re

DB_PATH = 'backend/data/map_data.db'
if not os.path.exists(DB_PATH):
    DB_PATH = 'data/map_data.db'

APT_PATH = 'data/apt_information.xlsx'

def extract_dong_jibun(addr_str):
    if not isinstance(addr_str, str):
        return None, None
    match = re.search(r'([가-힣a-zA-Z0-9]+[동가리])\s*([0-9-]+)', addr_str)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return None, None

def extract_road_building(addr_str):
    if not isinstance(addr_str, str):
        return None, None
    match = re.search(r'([가-힣a-zA-Z0-9]+[로길])\s*([0-9-]+)', addr_str)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return None, None

def update_households():
    if not os.path.exists(APT_PATH):
        print(f"Error: Could not find {APT_PATH}!")
        return

    print("Loading apt_information.xlsx...")
    df_apt = pd.read_excel(APT_PATH, header=1)
    print(f"Loaded {len(df_apt)} apartment rows.")
    
    # Build O(1) Hash Maps for lightning-fast matching
    print("Building high-performance hash maps...")
    jibun_hash_map = {}
    road_hash_map = {}
    danji_records = []
    
    for idx, row in df_apt.iterrows():
        h_val = row.get('세대수')
        if pd.isna(h_val) or h_val <= 0:
            continue
            
        danji = str(row.get('단지명', '')).strip()
        bop_addr = str(row.get('법정동주소', ''))
        road_addr = str(row.get('도로명주소', ''))
        
        dong, jibun = extract_dong_jibun(bop_addr)
        road, bld_no = extract_road_building(road_addr)
        
        households = int(h_val)
        
        if dong and jibun:
            jibun_hash_map[(dong, jibun)] = households
        if road and bld_no:
            road_hash_map[(road, bld_no)] = households
            
        danji_records.append({
            'danji': danji,
            'dong': dong,
            'households': households
        })
        
    print(f"Hash maps created. Jibun keys: {len(jibun_hash_map)}, Road keys: {len(road_hash_map)}")
    
    print(f"Connecting to DB: {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, address, property_type, households FROM auctions")
    auctions = cursor.fetchall()
    print(f"Loaded {len(auctions)} auction properties from database.")
    
    updated_count = 0
    match_by_jibun = 0
    match_by_road = 0
    match_by_danji = 0
    
    batch_updates = []
    
    for row_id, address, p_type, curr_h in auctions:
        auc_dong, auc_jibun = extract_dong_jibun(address)
        auc_road, auc_bld = extract_road_building(address)
        
        matched_h = None
        
        # 1. O(1) Jibun lookup
        if auc_dong and auc_jibun:
            key = (auc_dong, auc_jibun)
            if key in jibun_hash_map:
                matched_h = jibun_hash_map[key]
                match_by_jibun += 1
                
        # 2. O(1) Road lookup
        if matched_h is None and auc_road and auc_bld:
            key = (auc_road, auc_bld)
            if key in road_hash_map:
                matched_h = road_hash_map[key]
                match_by_road += 1
                
        # 3. Fallback: unique Danji name within the address string
        if matched_h is None:
            if any(k in str(p_type) for k in ['아파트', '다세대', '오피스텔', '집합']):
                address_clean = address.replace(" ", "")
                for apt in danji_records:
                    danji_clean = apt['danji'].replace(" ", "")
                    if len(danji_clean) >= 5 and danji_clean in address_clean:
                        if address[:6] in apt['danji'] or address[:10] in apt['danji'] or (apt['dong'] and apt['dong'] in address):
                            matched_h = apt['households']
                            match_by_danji += 1
                            break
                            
        if matched_h is not None:
            if updated_count < 10:
                print(f"Matching: '{address}' -> Matched Households: {matched_h}")
            batch_updates.append((matched_h, row_id))
            updated_count += 1
            
    if batch_updates:
        print(f"Executing batch update of {len(batch_updates)} properties in DB...")
        cursor.executemany("UPDATE auctions SET households = ? WHERE id = ?", batch_updates)
        conn.commit()
        
    conn.close()
    
    print("\n=== Matching Stats ===")
    print(f"Total updated: {updated_count} rows.")
    print(f"  - Matched by Dong+Jibun: {match_by_jibun}")
    print(f"  - Matched by Road+Bld: {match_by_road}")
    print(f"  - Matched by Danji Name: {match_by_danji}")
    print("Apartment households update complete!")

if __name__ == "__main__":
    import time
    start = time.time()
    update_households()
    print(f"Finished in {time.time() - start:.2f} seconds.")
