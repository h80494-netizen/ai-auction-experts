import sqlite3
import os

def update_official_prices():
    main_db = os.path.abspath('backend/data/map_data.db')
    temp_db = os.path.abspath('deploy_temp/backend/data/map_data.db')
    
    db_paths = [main_db, temp_db]
    print("Target DB Paths:")
    for p in db_paths:
        print(" -", p, "Exists:", os.path.exists(p))
        
    # 1. Build a lookup dict from temp_db if it has valid official_land_price > 0
    price_lookup = {}
    if os.path.exists(temp_db):
        conn_t = sqlite3.connect(temp_db)
        cur_t = conn_t.cursor()
        cur_t.execute("SELECT case_no, address, official_land_price FROM auctions WHERE official_land_price > 0")
        for row in cur_t.fetchall():
            case_no, address, price = row
            key = (case_no.strip(), address.strip())
            price_lookup[key] = price
        conn_t.close()
        print(f"Loaded {len(price_lookup)} valid official_land_prices from deploy_temp DB lookup.")

    # 2. Update both DBs
    for db_path in db_paths:
        if not os.path.exists(db_path):
            continue
            
        print(f"\nProcessing DB: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check target rows
        cursor.execute("SELECT id, case_no, property_type, address, appraisal_price, official_land_price FROM auctions")
        all_auctions = cursor.fetchall()
        
        updated_count = 0
        from_lookup_count = 0
        estimated_count = 0
        
        for item in all_auctions:
            auc_id, case_no, prop_type, address, appraisal_price, current_price = item
            
            # If current_price is 0 or NULL
            if current_price is None or current_price == 0:
                key = (str(case_no).strip(), str(address).strip())
                new_price = 0.0
                
                # Try lookup
                if key in price_lookup:
                    new_price = price_lookup[key]
                    from_lookup_count += 1
                else:
                    # Estimate based on appraisal_price (68% ratio for villas/houses, 70% for others)
                    if appraisal_price and appraisal_price > 0:
                        ratio = 0.68 if ('다세대' in str(prop_type) or '연립' in str(prop_type) or '빌라' in str(prop_type)) else 0.70
                        new_price = round(appraisal_price * ratio, -4) # round to 10,000 KRW
                        estimated_count += 1
                
                if new_price > 0:
                    cursor.execute("UPDATE auctions SET official_land_price = ? WHERE id = ?", (new_price, auc_id))
                    updated_count += 1
                    
        conn.commit()
        
        # Verify stats after update
        total_auctions = cursor.execute("SELECT count(*) FROM auctions").fetchone()[0]
        nonzero_price = cursor.execute("SELECT count(*) FROM auctions WHERE official_land_price > 0").fetchone()[0]
        villa_nonzero = cursor.execute("SELECT count(*) FROM auctions WHERE (property_type LIKE '%다세대%' OR property_type LIKE '%연립%') AND official_land_price > 0").fetchone()[0]
        villa_total = cursor.execute("SELECT count(*) FROM auctions WHERE (property_type LIKE '%다세대%' OR property_type LIKE '%연립%')").fetchone()[0]
        
        conn.close()
        
        print(f"=== Update Complete for {os.path.basename(db_path)} ===")
        print(f"  Total Updated: {updated_count} (From Temp DB Lookup: {from_lookup_count}, Estimated: {estimated_count})")
        print(f"  Total Auctions: {total_auctions} | Non-zero Official Price: {nonzero_price} ({nonzero_price/total_auctions*100:.1f}%)")
        print(f"  Villa Total: {villa_total} | Non-zero Official Price: {villa_nonzero} ({villa_nonzero/villa_total*100:.1f}%)\n")

if __name__ == '__main__':
    update_official_prices()
