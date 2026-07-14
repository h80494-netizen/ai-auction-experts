import requests
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

base_key = "babef8969e9c4d1884b50ea5e4fbee8"
chars = "0123456789abcdef"
url = "https://openapi.gg.go.kr/TBGRISCTYRVBSNSM"
headers = {"User-Agent": "Mozilla/5.0"}

def try_key(key):
    try:
        res = requests.get(url, params={"KEY": key, "Type": "json", "pIndex": 1, "pSize": 1}, headers=headers, verify=False, timeout=2)
        if "ERROR-290" not in res.text:
            return key, res.text
    except Exception:
        pass
    return None

def main():
    print("Generating 512 key combinations...")
    combinations = []
    for i in range(len(base_key) + 1):
        for c in chars:
            candidate = base_key[:i] + c + base_key[i:]
            combinations.append(candidate)
            
    # Remove duplicates
    combinations = list(set(combinations))
    print(f"Testing {len(combinations)} unique keys...")
    
    found = None
    # Use ThreadPoolExecutor to run tests in parallel
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(try_key, k): k for k in combinations}
        for fut in as_completed(futures):
            result = fut.result()
            if result:
                found = result
                print(f"\n[SUCCESS] Found working key: {result[0]}")
                print("Response:", result[1][:500])
                # Cancel other futures
                break
                
    if not found:
        print("\nBrute-force finished. No working key found.")

if __name__ == "__main__":
    main()
