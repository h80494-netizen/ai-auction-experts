import sys
import os
import pprint

# Reconfigure stdout to use utf-8 to prevent UnicodeEncodeError on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))

from app import get_map_demographics

# Coordinates for 은평구 수색동 (approximate)
lat, lng = 37.5816, 126.8972

tests = [
    {
        "name": "Case 1: Large Property (2025 타경 1005 style: 117.8평, no floor in address)",
        "address": "서울특별시 은평구 수색동 106-6 외 4필지",
        "area_size": 117.8
    },
    {
        "name": "Case 2: Small Basement Property (10평, 지하 1층)",
        "address": "서울특별시 마포구 합정동 300-1 지하 1층",
        "area_size": 10.5
    },
    {
        "name": "Case 3: Upper Floor Medium Property (30평, 3층)",
        "address": "경기도 성남시 분당구 삼평동 601 3층 302호",
        "area_size": 30.0
    },
    {
        "name": "Case 4: Office Area - Ground Floor Small (8평, 1층)",
        "address": "서울특별시 강남구 역삼동 700 1층",
        "area_size": 8.0
    }
]

print("Starting Custom Recommendation Matrix Verification Tests...\n")

for i, test in enumerate(tests, 1):
    print(f"============================================================")
    print(f"TEST {i}: {test['name']}")
    print(f"Address: {test['address']}")
    print(f"Area Size: {test['area_size']} py")
    print(f"------------------------------------------------------------")
    
    # We will use coordinates:
    # For Case 4, we use Gangnam coordinates (office heavy)
    if "Office Area" in test['name']:
        test_lat, test_lng = 37.4979, 127.0276 # Gangnam
    else:
        test_lat, test_lng = lat, lng # Eunpyeong (Residential heavy)
        
    res = get_map_demographics(test_lat, test_lng, address=test['address'], area_size=test['area_size'])
    
    if res.get("status") == "success":
        assessment = res.get("assessment", {})
        print(f"Demand Assessment: {assessment.get('class')}")
        print(f"Recommended Business (recom_biz): {assessment.get('recom_biz')}")
        print(f"Recommendation Details (recom_desc):\n{assessment.get('recom_desc')}")
    else:
        print(f"Error: {res}")
    print(f"============================================================\n")
