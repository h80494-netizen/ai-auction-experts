import requests
import json

url = "http://localhost:8000/api/issues?region=광도면"
try:
    res = requests.get(url, timeout=10)
    print("Status:", res.status_code)
    print("Response:", json.dumps(res.json(), ensure_ascii=False, indent=2)[:500])
except Exception as e:
    print("Error:", e)
