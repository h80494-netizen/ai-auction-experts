import sys
import os
import json
import sqlite3

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from ai_analyzer import generate_comparison_analysis, run_deterministic_comparison_fallback

def test_compare():
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend/data/map_data.db'))
    print("DB Path:", db_path)
    if not os.path.exists(db_path):
        print("Database not found!")
        return
        
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Query 3 sample auctions
    cursor.execute("SELECT * FROM auctions LIMIT 3")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    if not rows:
        print("No sample auctions found in database!")
        return
        
    print(f"Loaded {len(rows)} sample auctions.")
    for idx, r in enumerate(rows):
        print(f"Sample {idx+1}: {r['case_no']} - {r['address']} (Appraisal: {r['appraisal_price']:,} Won, Min: {r['min_price']:,} Won)")
        
    print("\n--- Running Fallback Analysis (Deterministic) ---")
    fallback_res = run_deterministic_comparison_fallback(rows)
    print(json.dumps(json.loads(fallback_res), indent=2, ensure_ascii=False))
    
    print("\n--- Running Gemini AI Analysis ---")
    ai_res = generate_comparison_analysis(rows)
    print(ai_res)

if __name__ == "__main__":
    test_compare()
