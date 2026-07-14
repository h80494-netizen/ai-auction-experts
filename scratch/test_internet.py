import requests

try:
    print("Testing internet connection to google.com...")
    r = requests.get("https://www.google.com", timeout=5)
    print("Status:", r.status_code)
    print("Length of response:", len(r.text))
except Exception as e:
    print("Error:", e)
