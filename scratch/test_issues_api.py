import urllib.request
import json
import sys

# Reconfigure stdout to use utf-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

url = "http://127.0.0.1:8000/api/issues?region=%EC%84%9C%EB%8C%80%EB%AC%B8%EA%B5%AC" # Urlencoded 서대문구
try:
    print(f"Querying {url}...")
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        data = json.loads(html)
        
        print("\nAPI Response status:", data.get('status'))
        if data.get('status') == 'success':
            issues = data.get('data', [])
            print(f"Total issues returned: {len(issues)}")
            for idx, issue in enumerate(issues):
                print(f"\n[{idx+1}] {issue.get('title')}")
                print(f"  Source: {issue.get('source')}")
                print(f"  Date: {issue.get('scanned_date')}")
                print(f"  Keywords: {issue.get('keywords')}")
                print(f"  Status: {issue.get('status_label')}")
                print(f"  Description: {issue.get('description')[:120]}...")
        else:
            print("Error in API response:", data.get('message'))
except Exception as e:
    print("Failed to query API:", e)
