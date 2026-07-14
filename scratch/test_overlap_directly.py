import requests
import json

url = "http://localhost:8000/api/map/overlap_analyze"
payload = {
    "case_nos": [
        "2023 타경 503633",
        "2024 타경 12431(5)",
        "2024 타경 14758"
    ]
}

headers = {
    "Content-Type": "application/json"
}

try:
    print("Sending POST request to /api/map/overlap_analyze...")
    res = requests.post(url, json=payload, headers=headers, timeout=60)
    print("Status Code:", res.status_code)
    data = res.json()
    print("Response keys:", list(data.keys()))
    if data.get("status") == "success":
        print("\nGemini Overlap Report Preview:")
        print(data.get("report")[:800])
        print("\nParsed items count:", len(data.get("items")))
    else:
        print("Error message:", data.get("message"))
except Exception as e:
    print("Error:", e)
