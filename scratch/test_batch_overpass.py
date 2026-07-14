import sqlite3
import requests
import json
import time
import re

DB_PATH = 'backend/data/map_data.db'
urls = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter"
]
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "http://localhost:8000/"
}

def test_batch():
    # Let's pick 5 uncached Gyeonggi cells
    # E.g. cells around (3720, 12683), (3720, 12684), (3721, 12683), (3721, 12684), (3722, 12683)
    test_cells = [
        (3720, 12683),
        (3720, 12684),
        (3721, 12683),
        (3721, 12684),
        (3722, 12683)
    ]
    
    print("Building batch Overpass QL query...")
    bbox_queries = []
    for cell_lat, cell_lng in test_cells:
        c_min_lat = cell_lat * 0.01
        c_max_lat = (cell_lat + 1) * 0.01
        c_min_lng = cell_lng * 0.01
        c_max_lng = (cell_lng + 1) * 0.01
        bbox_queries.append(f'way["highway"~"residential|service|unclassified|pedestrian|path|footway|living_street"]({c_min_lat},{c_min_lng},{c_max_lat},{c_max_lng});')
        
    query = f"""
    [out:json][timeout:30];
    (
      {" ".join(bbox_queries)}
    );
    out geom;
    """
    
    print("Query:")
    print(query)
    
    success = False
    for url in urls:
        try:
            print(f"Sending request to {url}...")
            t0 = time.time()
            res = requests.post(url, data={"data": query}, headers=headers, timeout=25.0)
            print(f"Response status: {res.status_code}, time taken: {time.time() - t0:.2f}s")
            if res.status_code == 200:
                data = res.json()
                elements = data.get("elements", [])
                print(f"Success! Returned {len(elements)} elements.")
                success = True
                break
        except Exception as e:
            print(f"Error for {url}: {e}")
            
    if not success:
        print("Batch fetch failed for all mirrors.")

if __name__ == "__main__":
    test_batch()
