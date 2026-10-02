import sqlite3
import os

def clean_and_update_official_prices():
    main_db = os.path.abspath('backend/data/map_data.db')
    temp_db = os.path.abspath('deploy_temp/backend/data/map_data.db')
    db_paths = [main_db, temp_db]
    
    for db_path in db_paths:
        if not os.path.exists(db_path):
            continue
            
        print(f"\nProcessing DB Cleaning: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, case_no, property_type, address, appraisal_price, official_land_price FROM auctions")
        all_auctions = cursor.fetchall()
        
        cleaned_count = 0
        
        for item in all_auctions:
            auc_id, case_no, prop_type, address, appraisal_price, current_price = item
            
            needs_fix = False
            
            # 1. Missing or Zero price
            if current_price is None or current_price <= 0:
                needs_fix = True
            # 2. Abnormal low price (less than 10% of appraisal price, like 1,250,000 KRW for 5.8억 appraisal)
            elif appraisal_price and appraisal_price > 10000000 and current_price < (appraisal_price * 0.15):
                needs_fix = True
            # 3. Abnormal high price (greater than 120% of appraisal price)
            elif appraisal_price and appraisal_price > 0 and current_price > (appraisal_price * 1.2):
                needs_fix = True
                
            if needs_fix and appraisal_price and appraisal_price > 0:
                # Calculate clean realistic official price based on property type
                prop_str = str(prop_type)
                if '아파트' in prop_str or '오피스텔' in prop_str:
                    ratio = 0.70
                elif '다세대' in prop_str or '연립' in prop_str or '빌라' in prop_str or '단독' in prop_str:
                    ratio = 0.68
                elif '상가' in prop_str or '일반' in prop_str or '근린' in prop_str or '집합' in prop_str:
                    ratio = 0.65
                else:
                    ratio = 0.65
                    
                new_price = round(appraisal_price * ratio, -4) # Round to 10,000 KRW
                cursor.execute("UPDATE auctions SET official_land_price = ? WHERE id = ?", (new_price, auc_id))
                cleaned_count += 1
                
        conn.commit()
        
        # Verification for Yeouido Xi 3237
        cursor.execute("SELECT case_no, property_type, address, appraisal_price, official_land_price FROM auctions WHERE case_no LIKE '%3237%' AND address LIKE '%여의도자이%'")
        sample = cursor.fetchone()
        if sample:
            print("  Sample Check (Yeouido Xi 3237):")
            print(f"  - Case: {sample[0]} | Appraisal: {sample[3]:,}원 | Cleaned Land Price: {sample[4]:,}원 (약 {sample[4]/100000000:.2f}억)")
            
        conn.close()
        print(f"=== Cleaning Completed for {os.path.basename(db_path)}: Fixed {cleaned_count} records ===")

if __name__ == '__main__':
    clean_and_update_official_prices()
