import requests
import json

url = "http://localhost:8000/api/map/overlap_analyze"
payload = {
    # Using the exact case_no format stored in the DB: '2024 타경 3031'
    "case_nos": ["2024 타경 3031"],
    "scores": {"2024 타경 3031": 85},
    "overlap_counts": {"2024 타경 3031": 3},
    "matched_layers": {"2024 타경 3031": ["지하철역", "대학교", "상권"]}
}

try:
    print("Sending POST request to /api/map/overlap_analyze with correct case number...")
    res = requests.post(url, json=payload, timeout=20)
    print("Status Code:", res.status_code)
    print("Response JSON:")
    print(json.dumps(res.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print("Error querying API:", e)
