import requests

try:
    res = requests.get("http://localhost:8000/", timeout=3)
    print("Status:", res.status_code)
    print("Content preview:", res.text[:200])
except Exception as e:
    print("Error:", e)
