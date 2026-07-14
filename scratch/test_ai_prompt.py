import os
import sys

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from ai_analyzer import generate_deep_research

# Test Case 1: Apartment (주택 - 아파트)
apartment_data = {
    "case_number": "2024타경5020",
    "address": "경기도 남양주시 퇴계원읍 도제원로 84, 101동 17층1702호 (신도아파트)",
    "property_type": "아파트",
    "appraised_value": 407000000,
    "minimum_value": 284900000,
    "approval_date": "2000-10-15",
    "auction_date": "2026-06-15",
    "land_area": "11.72평",
    "building_area": "25.59평",
    "risks": [],
    "precautions": "특이사항 없음",
    "is_regulated_area": False,
    "house_count": "1주택",
    "investor_type": "개인",
    "investment_duration": "장기(3년, 임대전략)",
    "target_return": "20",
    "has_tenant": False,
    "pdf_text": """
    [감정평가서 발췌]
    본 건은 경기도 남양주시 퇴계원읍 소재 신도아파트 101동 1702호로서,
    방 3개, 욕실/화장실 2개, 거실, 주방 등으로 구성되어 있음.
    거실 기준 남향이며, 복도식/계단식 구분 중 계단식 아파트임.
    승강기(엘리베이터) 설비가 되어 있으며, 도시가스에 의한 개별난방 방식을 채택하고 있음.
    """
}

# Test Case 2: Commercial Property (상가)
commercial_data = {
    "case_number": "2024타경9999",
    "address": "서울특별시 강남구 테헤란로 123, 1층 101호",
    "property_type": "근린상가",
    "appraised_value": 1000000000,
    "minimum_value": 800000000,
    "approval_date": "2015-05-20",
    "auction_date": "2026-06-15",
    "land_area": "5평",
    "building_area": "15평",
    "risks": [],
    "precautions": "특이사항 없음",
    "is_regulated_area": False,
    "house_count": "무주택",
    "investor_type": "개인",
    "investment_duration": "단기(6개월)",
    "target_return": "20",
    "has_tenant": False,
    "pdf_text": """
    [감정평가서 발췌]
    본 건은 서울특별시 강남구 역삼동 소재 근린생활시설(상가)로서,
    현황 공실이며, 개별 냉난방 설비가 설치되어 있음. 엘리베이터 설치됨.
    """
}

print("=== Running Case 1: Apartment ===")
res1 = generate_deep_research(apartment_data)
print(res1)
print("\n" + "="*50 + "\n")

print("=== Running Case 2: Commercial Property ===")
res2 = generate_deep_research(commercial_data)
print(res2)
