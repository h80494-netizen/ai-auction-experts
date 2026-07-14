import urllib.request
import json

def test_issues(name, query):
    url = f"http://localhost:8000/api/issues?region={urllib.parse.quote(query)}"
    print(f"\n--- Testing {name} (Query: '{query}') ---")
    print(f"URL: {url}")
    try:
        response = urllib.request.urlopen(url, timeout=10)
        res_data = json.loads(response.read().decode('utf-8'))
        status = res_data.get("status")
        print(f"Status: {status}")
        if status == "success":
            issues = res_data.get("data", [])
            print(f"Number of issues returned: {len(issues)}")
            if issues:
                print("First issue title:", issues[0].get("title"))
                print("First issue region:", issues[0].get("region"))
            else:
                print("No issues found.")
        else:
            print("ERROR: API returned failure status")
    except Exception as e:
        print("ERROR: Request failed:", e)

# 1. Search '서울'
test_issues("Seoul Search", "서울")

# 2. Search '경기'
test_issues("Gyeonggi Search", "경기")

# 3. Search '경기지역'
test_issues("Gyeonggi Area Search", "경기지역")

# 4. Search '경기도'
test_issues("Gyeonggi Province Full Search", "경기도")

# 5. Search '서울시'
test_issues("Seoul City Search", "서울시")

# 6. Search '인천시'
test_issues("Incheon City Search", "인천시")
