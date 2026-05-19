import sys
import asyncio
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from backend.ai_analyzer import generate_deep_research

test_data = {
    "case_number": "2024타경1234",
    "address": "서울 용산구",
    "property_type": "아파트",
    "minimum_value": 500000000,
    "appraised_value": 700000000,
    "risks": ["대항력 임차인"]
}

try:
    res = generate_deep_research(test_data)
    print("Success. Result length:", len(res))
    print(res)
except Exception as e:
    print(f"Error: {e}")
