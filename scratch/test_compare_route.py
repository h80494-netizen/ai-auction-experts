import sys
import os
import asyncio
import json

# Add backend dir to sys.path
sys.path.append(os.path.abspath("backend"))

from app import compare_auctions, CompareRequest

async def test_route():
    # Retrieve some sample case numbers from the database
    import sqlite3
    db_path = os.path.abspath("backend/data/map_data.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT case_no FROM auctions LIMIT 3")
    cases = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    if not cases:
        print("No cases found in DB!")
        return
        
    print(f"Testing route with cases: {cases}")
    
    # Construct request payload
    req = CompareRequest(case_numbers=cases)
    
    # Call compare_auctions directly (it is an async function)
    response = await compare_auctions(req)
    print("Response Status:", response.get("status"))
    if response.get("status") == "success":
        data = response.get("data")
        print("\n=== COMPARISON TABLE ===")
        print(json.dumps(data.get("comparison_table"), indent=2, ensure_ascii=False))
        print("\n=== RECOMMENDATIONS ===")
        print(json.dumps(data.get("recommendations"), indent=2, ensure_ascii=False))
    else:
        print("Response error message:", response.get("message"))

if __name__ == "__main__":
    asyncio.run(test_route())
