import sys
import os

# Add backend to python path
sys.path.append(os.path.abspath('backend'))

from ai_analyzer import analyze_overlap_cases

fake_items = [
    {
        'case_no': '2023타경12345',
        'address': '경기도 성남시 분당구 정자동 123',
        'property_type': '아파트',
        'appraised_value': 1000000000,
        'minimum_value': 800000000,
        'min_bid_rate': 80,
        'score': 85,
        'overlap_count': 3,
        'matched_layers': ['지하철역', '용도지역', '재개발/재건축'],
        'special_notes': '임차인 대항력 있음',
        'area_size': 84.9,
        'land_size': 45.2,
        'subway_dist': 250,
        'official_land_price': 5000000,
        'min_price_per_pyeong': 25000000
    }
]

print("Calling analyze_overlap_cases...")
try:
    res = analyze_overlap_cases(fake_items)
    print("Result:")
    print(res)
except Exception as e:
    print("Error occurred:")
    print(e)
