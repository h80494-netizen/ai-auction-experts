import requests
import json

url = "http://localhost:8000/api/map/overlap_analyze"
payload = {
    "case_nos": ["2024타경5020"],
    "scores": {"2024타경5020": 85},
    "overlap_counts": {"2024타경5020": 3},
    "matched_layers": {"2024타경5020": ["지하철역", "대학교", "상권"]}
}

try:
    print("Sending POST request to /api/map/overlap_analyze...")
    res = requests.post(url, json=payload, timeout=15)
    print("Status Code:", res.status_code)
    print("Response JSON:")
    print(json.dumps(res.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print("Error querying API:", e)
