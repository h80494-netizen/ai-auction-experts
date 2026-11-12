# -*- coding: utf-8 -*-
"""
소상공인 상권 10대 대분류 및 세부업종 동적 지표 레지스트리 (Dynamic Config Registry)
- small_business.db 의 (cat_large_name, cat_medium_name, cat_small_name, name) 실데이터를
  표준 세부업종으로 정규화 분류하고,
- 업종별 기준 월 카드매출, 월 결제건수, 카드결제 비중(card_share),
  결제건당 방문·출석·내방 환산계수(visitors_per_tx)를 통해
  [업소당 하루 평균 방문자 수 (명/일)]를 일관되게 산출합니다.
"""

from typing import Dict, List, Any, Tuple


# 세부업종별 동적 단위경제 설정 레지스트리
# sales_man: 점포당 월평균 카드매출(만원)
# tx_cnt: 점포당 월평균 카드결제 건수(건)
# card_share: 전체 거래 중 카드결제 비중 (0~1)
# visitors_per_tx: 결제 1건당 실방문객 환산 계수 (동반인원 또는 정기권 다회 출석/내방상담 반영)
SUBCATEGORY_CONFIG_REGISTRY: Dict[str, Dict[str, Any]] = {
    # ==================== 1. 음식 ====================
    "한식 · 백반 · 국탕류": {
        "large": "음식", "icon": "fa-bowl-rice",
        "sales_man": 2350, "tx_cnt": 810, "card_share": 0.92, "visitors_per_tx": 2.05
    },
    "구이 · 고기 · 해산물": {
        "large": "음식", "icon": "fa-fire-burner",
        "sales_man": 3400, "tx_cnt": 520, "card_share": 0.93, "visitors_per_tx": 2.85
    },
    "카페 · 커피 · 음료": {
        "large": "음식", "icon": "fa-mug-hot",
        "sales_man": 1620, "tx_cnt": 2350, "card_share": 0.94, "visitors_per_tx": 1.22
    },
    "분식 · 김밥 · 샌드위치": {
        "large": "음식", "icon": "fa-utensils",
        "sales_man": 1720, "tx_cnt": 1420, "card_share": 0.92, "visitors_per_tx": 1.35
    },
    "베이커리 · 디저트 · 떡": {
        "large": "음식", "icon": "fa-bread-slice",
        "sales_man": 1950, "tx_cnt": 1520, "card_share": 0.93, "visitors_per_tx": 1.20
    },
    "치킨 · 피자 · 패스트푸드": {
        "large": "음식", "icon": "fa-burger",
        "sales_man": 2150, "tx_cnt": 1080, "card_share": 0.94, "visitors_per_tx": 1.45
    },
    "요리주점 · 호프 · 포차": {
        "large": "음식", "icon": "fa-beer-mug-empty",
        "sales_man": 2250, "tx_cnt": 450, "card_share": 0.93, "visitors_per_tx": 2.75
    },
    "일식 · 초밥 · 돈가스": {
        "large": "음식", "icon": "fa-fish",
        "sales_man": 2950, "tx_cnt": 780, "card_share": 0.94, "visitors_per_tx": 1.95
    },
    "양식 · 브런치 · 파스타": {
        "large": "음식", "icon": "fa-wine-glass",
        "sales_man": 2750, "tx_cnt": 720, "card_share": 0.94, "visitors_per_tx": 2.15
    },
    "중식 · 마라 · 아시안": {
        "large": "음식", "icon": "fa-bowl-food",
        "sales_man": 2450, "tx_cnt": 890, "card_share": 0.93, "visitors_per_tx": 1.85
    },
    "구내식당 · 뷔페": {
        "large": "음식", "icon": "fa-plate-wheat",
        "sales_man": 3800, "tx_cnt": 1650, "card_share": 0.88, "visitors_per_tx": 1.75
    },

    # ==================== 2. 소매 ====================
    "편의점": {
        "large": "소매", "icon": "fa-store",
        "sales_man": 4150, "tx_cnt": 6700, "card_share": 0.90, "visitors_per_tx": 1.08
    },
    "슈퍼마켓 · 식자재마트": {
        "large": "소매", "icon": "fa-cart-shopping",
        "sales_man": 4800, "tx_cnt": 2650, "card_share": 0.89, "visitors_per_tx": 1.20
    },
    "약국 · 의료기기": {
        "large": "소매", "icon": "fa-pills",
        "sales_man": 3650, "tx_cnt": 2100, "card_share": 0.88, "visitors_per_tx": 1.06
    },
    "화장품 · 뷰티스토어": {
        "large": "소매", "icon": "fa-spray-can-sparkles",
        "sales_man": 2300, "tx_cnt": 920, "card_share": 0.93, "visitors_per_tx": 1.25
    },
    "의류 · 패션 · 신발 · 잡화": {
        "large": "소매", "icon": "fa-shirt",
        "sales_man": 1680, "tx_cnt": 310, "card_share": 0.90, "visitors_per_tx": 1.65
    },
    "청과 · 정육 · 반찬 · 식료품": {
        "large": "소매", "icon": "fa-apple-whole",
        "sales_man": 2150, "tx_cnt": 940, "card_share": 0.82, "visitors_per_tx": 1.15
    },
    "휴대폰 · 가전 · 컴퓨터": {
        "large": "소매", "icon": "fa-mobile-screen-button",
        "sales_man": 2650, "tx_cnt": 240, "card_share": 0.85, "visitors_per_tx": 1.75
    },
    "문구 · 서점 · 스포츠 · 완구": {
        "large": "소매", "icon": "fa-book-open",
        "sales_man": 1580, "tx_cnt": 860, "card_share": 0.90, "visitors_per_tx": 1.30
    },
    "꽃집 · 화원 · 기프트샵": {
        "large": "소매", "icon": "fa-seedling",
        "sales_man": 1180, "tx_cnt": 290, "card_share": 0.86, "visitors_per_tx": 1.25
    },
    "생활용품 · 철물 · 주유/기타소매": {
        "large": "소매", "icon": "fa-boxes-stacked",
        "sales_man": 1950, "tx_cnt": 540, "card_share": 0.86, "visitors_per_tx": 1.18
    },

    # ==================== 3. 과학·기술 ====================
    "변호사 · 법무사 · 노무 · 특허": {
        "large": "과학·기술", "icon": "fa-scale-balanced",
        "sales_man": 2900, "tx_cnt": 85, "card_share": 0.45, "visitors_per_tx": 1.45
    },
    "세무사 · 공인회계사": {
        "large": "과학·기술", "icon": "fa-calculator",
        "sales_man": 2450, "tx_cnt": 110, "card_share": 0.45, "visitors_per_tx": 1.15
    },
    "경영 · 창업 · 비즈니스 컨설팅": {
        "large": "과학·기술", "icon": "fa-briefcase",
        "sales_man": 2350, "tx_cnt": 90, "card_share": 0.48, "visitors_per_tx": 1.15
    },
    "건축설계 · 토목 · 엔지니어링": {
        "large": "과학·기술", "icon": "fa-compass-drafting",
        "sales_man": 2750, "tx_cnt": 78, "card_share": 0.42, "visitors_per_tx": 1.10
    },
    "인테리어 · 시각 · 제품 디자인": {
        "large": "과학·기술", "icon": "fa-pen-ruler",
        "sales_man": 2150, "tx_cnt": 95, "card_share": 0.55, "visitors_per_tx": 1.25
    },
    "광고대행 · 마케팅 · 인쇄제작": {
        "large": "과학·기술", "icon": "fa-bullhorn",
        "sales_man": 2250, "tx_cnt": 125, "card_share": 0.58, "visitors_per_tx": 1.10
    },
    "사진관 · 스튜디오 촬영": {
        "large": "과학·기술", "icon": "fa-camera-retro",
        "sales_man": 1380, "tx_cnt": 295, "card_share": 0.92, "visitors_per_tx": 1.65
    },
    "번역 · 지식재산 · 전문과학 기타": {
        "large": "과학·기술", "icon": "fa-microscope",
        "sales_man": 1850, "tx_cnt": 92, "card_share": 0.55, "visitors_per_tx": 1.15
    },

    # ==================== 4. 예술·스포츠 ====================
    "헬스장 · 피트니스 · PT": {
        "large": "예술·스포츠", "icon": "fa-dumbbell",
        "sales_man": 2650, "tx_cnt": 165, "card_share": 0.90, "visitors_per_tx": 13.20
    },
    "골프연습장 · 스크린골프": {
        "large": "예술·스포츠", "icon": "fa-golf-ball-tee",
        "sales_man": 2450, "tx_cnt": 480, "card_share": 0.90, "visitors_per_tx": 2.20
    },
    "당구장 · 볼링 · 테니스 · 구기": {
        "large": "예술·스포츠", "icon": "fa-bowling-ball",
        "sales_man": 1480, "tx_cnt": 540, "card_share": 0.88, "visitors_per_tx": 2.35
    },
    "독서실 · 스터디카페": {
        "large": "예술·스포츠", "icon": "fa-book-open-reader",
        "sales_man": 1350, "tx_cnt": 420, "card_share": 0.94, "visitors_per_tx": 3.60
    },
    "노래연습장 · 코인노래방": {
        "large": "예술·스포츠", "icon": "fa-microphone-lines",
        "sales_man": 1280, "tx_cnt": 630, "card_share": 0.86, "visitors_per_tx": 2.30
    },
    "PC방 · 게임장 · 복합오락": {
        "large": "예술·스포츠", "icon": "fa-gamepad",
        "sales_man": 2100, "tx_cnt": 2150, "card_share": 0.91, "visitors_per_tx": 1.15
    },
    "복권 · 로또 판매점": {
        "large": "예술·스포츠", "icon": "fa-ticket",
        "sales_man": 2800, "tx_cnt": 2900, "card_share": 0.45, "visitors_per_tx": 1.02
    },

    # ==================== 5. 부동산 ====================
    "공인중개사사무소 (주거·상가)": {
        "large": "부동산", "icon": "fa-house-chimney-user",
        "sales_man": 920, "tx_cnt": 45, "card_share": 0.35, "visitors_per_tx": 1.80
    },
    "부동산 중개법인 · 상업용중개": {
        "large": "부동산", "icon": "fa-building-circle-check",
        "sales_man": 2350, "tx_cnt": 68, "card_share": 0.38, "visitors_per_tx": 1.75
    },
    "부동산 컨설팅 · 경매 · 투자자문": {
        "large": "부동산", "icon": "fa-chart-line",
        "sales_man": 1950, "tx_cnt": 56, "card_share": 0.42, "visitors_per_tx": 1.65
    },
    "부동산 임대 · 자산관리 · 분양": {
        "large": "부동산", "icon": "fa-key",
        "sales_man": 2450, "tx_cnt": 74, "card_share": 0.40, "visitors_per_tx": 1.35
    },

    # ==================== 6. 숙박 ====================
    "호텔 · 비즈니스호텔 · 리조트": {
        "large": "숙박", "icon": "fa-hotel",
        "sales_man": 6800, "tx_cnt": 620, "card_share": 0.85, "visitors_per_tx": 1.85
    },
    "모텔 · 일반숙박업": {
        "large": "숙박", "icon": "fa-bed",
        "sales_man": 2900, "tx_cnt": 580, "card_share": 0.82, "visitors_per_tx": 1.90
    },
    "고시원 · 원룸텔 · 레지던스": {
        "large": "숙박", "icon": "fa-building-user",
        "sales_man": 1420, "tx_cnt": 36, "card_share": 0.65, "visitors_per_tx": 14.50
    },
    "펜션 · 게스트하우스 · 민박": {
        "large": "숙박", "icon": "fa-campground",
        "sales_man": 1850, "tx_cnt": 165, "card_share": 0.84, "visitors_per_tx": 2.45
    },

    # ==================== 7. 시설관리·임대 ====================
    "건물청소 · 방역 · 소독 서비스": {
        "large": "시설관리·임대", "icon": "fa-broom",
        "sales_man": 1750, "tx_cnt": 92, "card_share": 0.55, "visitors_per_tx": 0.95
    },
    "인력공급 · 채용 · 고용알선": {
        "large": "시설관리·임대", "icon": "fa-people-group",
        "sales_man": 2150, "tx_cnt": 88, "card_share": 0.45, "visitors_per_tx": 1.55
    },
    "여행사 · 항공/투어 예약": {
        "large": "시설관리·임대", "icon": "fa-plane-departure",
        "sales_man": 2650, "tx_cnt": 115, "card_share": 0.78, "visitors_per_tx": 1.65
    },
    "전시 · 행사대행 · 사무지원": {
        "large": "시설관리·임대", "icon": "fa-clipboard-check",
        "sales_man": 1950, "tx_cnt": 140, "card_share": 0.68, "visitors_per_tx": 1.15
    },
    "빌딩 · 사업시설 유지관리 · 조경": {
        "large": "시설관리·임대", "icon": "fa-screwdriver-wrench",
        "sales_man": 2350, "tx_cnt": 82, "card_share": 0.48, "visitors_per_tx": 1.05
    },
    "렌터카 · 운송장비 대여": {
        "large": "시설관리·임대", "icon": "fa-car-side",
        "sales_man": 2850, "tx_cnt": 210, "card_share": 0.90, "visitors_per_tx": 1.45
    },
    "생활 · 레저 · 산업장비 렌탈": {
        "large": "시설관리·임대", "icon": "fa-toolbox",
        "sales_man": 1680, "tx_cnt": 175, "card_share": 0.82, "visitors_per_tx": 1.25
    },

    # ==================== 8. 수리·개인 ====================
    "미용실 · 헤어살롱 · 바버샵": {
        "large": "수리·개인", "icon": "fa-scissors",
        "sales_man": 1350, "tx_cnt": 310, "card_share": 0.88, "visitors_per_tx": 1.08
    },
    "피부관리 · 에스테틱": {
        "large": "수리·개인", "icon": "fa-spa",
        "sales_man": 1580, "tx_cnt": 165, "card_share": 0.88, "visitors_per_tx": 1.95
    },
    "네일 · 속눈썹 · 뷰티샵": {
        "large": "수리·개인", "icon": "fa-hand-sparkles",
        "sales_man": 1180, "tx_cnt": 215, "card_share": 0.86, "visitors_per_tx": 1.05
    },
    "자동차 정비 · 세차 · 외장관리": {
        "large": "수리·개인", "icon": "fa-car-wrench",
        "sales_man": 2350, "tx_cnt": 290, "card_share": 0.88, "visitors_per_tx": 1.15
    },
    "세탁소 · 코인빨래방": {
        "large": "수리·개인", "icon": "fa-jug-detergent",
        "sales_man": 980, "tx_cnt": 490, "card_share": 0.85, "visitors_per_tx": 1.05
    },
    "마사지 · 체형관리 · 사우나": {
        "large": "수리·개인", "icon": "fa-hot-tub-person",
        "sales_man": 1950, "tx_cnt": 420, "card_share": 0.86, "visitors_per_tx": 1.35
    },
    "의류수선 · 생활용품 수리": {
        "large": "수리·개인", "icon": "fa-shirt",
        "sales_man": 780, "tx_cnt": 270, "card_share": 0.78, "visitors_per_tx": 1.05
    },
    "컴퓨터 · 휴대폰 · 가전 수리": {
        "large": "수리·개인", "icon": "fa-screwdriver",
        "sales_man": 1450, "tx_cnt": 220, "card_share": 0.84, "visitors_per_tx": 1.12
    },
    "웨딩 · 상조 · 개인서비스 기타": {
        "large": "수리·개인", "icon": "fa-heart",
        "sales_man": 2400, "tx_cnt": 115, "card_share": 0.80, "visitors_per_tx": 1.85
    },

    # ==================== 9. 교육 ====================
    "입시 · 보습 · 교과학원": {
        "large": "교육", "icon": "fa-graduation-cap",
        "sales_man": 2450, "tx_cnt": 86, "card_share": 0.88, "visitors_per_tx": 14.50
    },
    "요가 · 필라테스 교육원": {
        "large": "교육", "icon": "fa-person-praying",
        "sales_man": 1850, "tx_cnt": 96, "card_share": 0.89, "visitors_per_tx": 11.50
    },
    "음악 · 미술 · 예체능학원": {
        "large": "교육", "icon": "fa-palette",
        "sales_man": 1680, "tx_cnt": 92, "card_share": 0.88, "visitors_per_tx": 12.20
    },
    "태권도 · 무술 · 유아체육학원": {
        "large": "교육", "icon": "fa-medal",
        "sales_man": 1920, "tx_cnt": 112, "card_share": 0.89, "visitors_per_tx": 13.80
    },
    "외국어 · 어학원": {
        "large": "교육", "icon": "fa-language",
        "sales_man": 2650, "tx_cnt": 98, "card_share": 0.90, "visitors_per_tx": 12.80
    },
    "직업훈련 · 코딩 · 자격증학원": {
        "large": "교육", "icon": "fa-laptop-code",
        "sales_man": 2550, "tx_cnt": 88, "card_share": 0.88, "visitors_per_tx": 11.50
    },
    "유학 · 진로 · 교육컨설팅": {
        "large": "교육", "icon": "fa-chalkboard-user",
        "sales_man": 1750, "tx_cnt": 65, "card_share": 0.80, "visitors_per_tx": 2.40
    },

    # ==================== 10. 보건의료 ====================
    "내과 · 소아과 · 일반의원": {
        "large": "보건의료", "icon": "fa-stethoscope",
        "sales_man": 3850, "tx_cnt": 1360, "card_share": 0.90, "visitors_per_tx": 1.15
    },
    "치과의원 · 치과병원": {
        "large": "보건의료", "icon": "fa-tooth",
        "sales_man": 4250, "tx_cnt": 530, "card_share": 0.90, "visitors_per_tx": 1.65
    },
    "한의원 · 한방병원": {
        "large": "보건의료", "icon": "fa-mortar-pestle",
        "sales_man": 2850, "tx_cnt": 690, "card_share": 0.90, "visitors_per_tx": 1.25
    },
    "피부과 · 성형외과 · 비뇨기과": {
        "large": "보건의료", "icon": "fa-wand-magic-sparkles",
        "sales_man": 5200, "tx_cnt": 480, "card_share": 0.92, "visitors_per_tx": 1.20
    },
    "정형외과 · 외과 · 통증의원": {
        "large": "보건의료", "icon": "fa-bone",
        "sales_man": 4300, "tx_cnt": 1120, "card_share": 0.90, "visitors_per_tx": 1.18
    },
    "신경과 · 정신건강의학과": {
        "large": "보건의료", "icon": "fa-brain",
        "sales_man": 3100, "tx_cnt": 640, "card_share": 0.90, "visitors_per_tx": 1.10
    },
    "종합병원 · 일반/요양병원": {
        "large": "보건의료", "icon": "fa-hospital",
        "sales_man": 9600, "tx_cnt": 2400, "card_share": 0.91, "visitors_per_tx": 1.45
    },
    "심리상담 · 체형교정 · 기타보건": {
        "large": "보건의료", "icon": "fa-hand-holding-medical",
        "sales_man": 1750, "tx_cnt": 210, "card_share": 0.86, "visitors_per_tx": 1.25
    },
}


# 대분류별 기본 폴백 세부업종 구성 (점포 목록이 비어있는 예외 상황에서 사용)
LARGE_CATEGORY_DEFAULT_SUBS: Dict[str, List[Tuple[str, float]]] = {
    "음식": [
        ("한식 · 백반 · 국탕류", 0.34),
        ("카페 · 커피 · 음료", 0.22),
        ("분식 · 김밥 · 샌드위치", 0.13),
        ("요리주점 · 호프 · 포차", 0.11),
        ("치킨 · 피자 · 패스트푸드", 0.10),
        ("일식 · 초밥 · 돈가스", 0.10),
    ],
    "소매": [
        ("편의점", 0.28),
        ("의류 · 패션 · 신발 · 잡화", 0.24),
        ("약국 · 의료기기", 0.14),
        ("화장품 · 뷰티스토어", 0.12),
        ("슈퍼마켓 · 식자재마트", 0.11),
        ("청과 · 정육 · 반찬 · 식료품", 0.11),
    ],
    "과학·기술": [
        ("경영 · 창업 · 비즈니스 컨설팅", 0.26),
        ("변호사 · 법무사 · 노무 · 특허", 0.18),
        ("광고대행 · 마케팅 · 인쇄제작", 0.18),
        ("건축설계 · 토목 · 엔지니어링", 0.14),
        ("세무사 · 공인회계사", 0.13),
        ("인테리어 · 시각 · 제품 디자인", 0.11),
    ],
    "예술·스포츠": [
        ("헬스장 · 피트니스 · PT", 0.32),
        ("골프연습장 · 스크린골프", 0.20),
        ("노래연습장 · 코인노래방", 0.15),
        ("독서실 · 스터디카페", 0.13),
        ("당구장 · 볼링 · 테니스 · 구기", 0.11),
        ("PC방 · 게임장 · 복합오락", 0.09),
    ],
    "부동산": [
        ("공인중개사사무소 (주거·상가)", 0.72),
        ("부동산 중개법인 · 상업용중개", 0.12),
        ("부동산 임대 · 자산관리 · 분양", 0.09),
        ("부동산 컨설팅 · 경매 · 투자자문", 0.07),
    ],
    "숙박": [
        ("모텔 · 일반숙박업", 0.44),
        ("고시원 · 원룸텔 · 레지던스", 0.24),
        ("호텔 · 비즈니스호텔 · 리조트", 0.18),
        ("펜션 · 게스트하우스 · 민박", 0.14),
    ],
    "시설관리·임대": [
        ("건물청소 · 방역 · 소독 서비스", 0.24),
        ("인력공급 · 채용 · 고용알선", 0.20),
        ("여행사 · 항공/투어 예약", 0.17),
        ("전시 · 행사대행 · 사무지원", 0.15),
        ("생활 · 레저 · 산업장비 렌탈", 0.13),
        ("렌터카 · 운송장비 대여", 0.11),
    ],
    "수리·개인": [
        ("미용실 · 헤어살롱 · 바버샵", 0.36),
        ("피부관리 · 에스테틱", 0.18),
        ("네일 · 속눈썹 · 뷰티샵", 0.12),
        ("자동차 정비 · 세차 · 외장관리", 0.12),
        ("세탁소 · 코인빨래방", 0.11),
        ("마사지 · 체형관리 · 사우나", 0.11),
    ],
    "교육": [
        ("입시 · 보습 · 교과학원", 0.40),
        ("음악 · 미술 · 예체능학원", 0.18),
        ("요가 · 필라테스 교육원", 0.14),
        ("외국어 · 어학원", 0.10),
        ("태권도 · 무술 · 유아체육학원", 0.10),
        ("직업훈련 · 코딩 · 자격증학원", 0.08),
    ],
    "보건의료": [
        ("내과 · 소아과 · 일반의원", 0.30),
        ("치과의원 · 치과병원", 0.22),
        ("피부과 · 성형외과 · 비뇨기과", 0.20),
        ("한의원 · 한방병원", 0.15),
        ("정형외과 · 외과 · 통증의원", 0.08),
        ("종합병원 · 일반/요양병원", 0.05),
    ],
}


def calc_daily_visitors_per_store(tx_per_store_monthly: float, card_share: float, visitors_per_tx: float) -> float:
    """
    업소당 하루 평균 방문자 수 (명/일) 산출:
      (월 카드결제 건수 / 카드결제 비중) * 건당 방문·출석·내방 환산계수 / 30일
    """
    safe_card_share = max(0.25, min(1.0, card_share or 0.9))
    daily_visits = ((tx_per_store_monthly / safe_card_share) * (visitors_per_tx or 1.1)) / 30.0
    return round(max(1.0, daily_visits), 1)


def resolve_subcategory(
    cat_large: str,
    cat_medium: str,
    cat_small: str,
    store_name: str = ""
) -> str:
    """
    small_business 테이블의 (대분류, 중분류, 소분류, 상호명)을
    SUBCATEGORY_CONFIG_REGISTRY 의 표준 세부업종 키로 매핑합니다.
    """
    l = (cat_large or "").strip()
    m = (cat_medium or "").strip()
    s = (cat_small or "").strip()
    nm = (store_name or "").strip()

    # 1. 음식
    if "음식" in l or "요식" in l:
        if "비알코올" in m or "비알콜" in m or "카페" in s or "커피" in s:
            return "카페 · 커피 · 음료"
        if "주점" in m or "주점" in s or "생맥주" in s:
            return "요리주점 · 호프 · 포차"
        if "일식" in m or "일식" in s or "초밥" in s:
            return "일식 · 초밥 · 돈가스"
        if "서양식" in m or "양식" in s or "파스타" in s or "스테이크" in s or "레스토랑" in s:
            return "양식 · 브런치 · 파스타"
        if "중식" in m or "중국" in s or "마라" in s or "동남아" in m or "베트남" in s or "외국" in m:
            return "중식 · 마라 · 아시안"
        if "구내식당" in m or "뷔페" in m or "구내식당" in s or "뷔페" in s:
            return "구내식당 · 뷔페"
        if "기타 간이" in m or "간이" in m:
            if "빵" in s or "도넛" in s or "제과" in s or "떡" in s or "한과" in s:
                return "베이커리 · 디저트 · 떡"
            if "치킨" in s or "피자" in s or "버거" in s:
                return "치킨 · 피자 · 패스트푸드"
            return "분식 · 김밥 · 샌드위치"
        if any(k in s for k in ("구이", "고기", "족발", "보쌈", "횟집", "해산물", "곱창")):
            return "구이 · 고기 · 해산물"
        return "한식 · 백반 · 국탕류"

    # 2. 소매
    if "소매" in l:
        if "편의점" in s:
            return "편의점"
        if "종합 소매" in m or "슈퍼" in s:
            return "슈퍼마켓 · 식자재마트"
        if "약국" in s or "의료기기" in s:
            return "약국 · 의료기기"
        if "화장품" in s or "의약·화장품" in m:
            return "화장품 · 뷰티스토어"
        if "섬유" in m or "의복" in m or "의류" in s or "신발" in s or "가방" in s or "잡화" in s:
            return "의류 · 패션 · 신발 · 잡화"
        if "식료품" in m or "정육" in s or "청과" in s or "채소" in s or "수산" in s or "반찬" in s:
            return "청과 · 정육 · 반찬 · 식료품"
        if "가전" in m or "통신" in m or "핸드폰" in s or "컴퓨터" in s:
            return "휴대폰 · 가전 · 컴퓨터"
        if "오락용품" in m or "문구" in s or "서점" in s or "운동용품" in s or "장난감" in s:
            return "문구 · 서점 · 스포츠 · 완구"
        if "식물" in m or "꽃" in s or "장식품" in m or "기념품" in s:
            return "꽃집 · 화원 · 기프트샵"
        return "생활용품 · 철물 · 주유/기타소매"

    # 3. 과학·기술
    if "과학" in l or "기술" in l:
        if "법무" in m or any(k in s for k in ("변호사", "법무사", "변리사", "행정사", "노무사")):
            return "변호사 · 법무사 · 노무 · 특허"
        if "회계" in m or "세무" in m or "세무사" in s or "회계사" in s:
            return "세무사 · 공인회계사"
        if "컨설팅" in m or "시장 조사" in m or "컨설팅" in s:
            return "경영 · 창업 · 비즈니스 컨설팅"
        if "기술 서비스" in m or "건축" in s or "엔지니어링" in s or "설계" in s:
            return "건축설계 · 토목 · 엔지니어링"
        if "디자인" in m or "디자인" in s:
            return "인테리어 · 시각 · 제품 디자인"
        if "광고" in m or "인쇄" in m or "광고" in s or "명함" in s or "간판" in s:
            return "광고대행 · 마케팅 · 인쇄제작"
        if "사진" in m or "사진" in s:
            return "사진관 · 스튜디오 촬영"
        return "번역 · 지식재산 · 전문과학 기타"

    # 4. 예술·스포츠
    if "예술" in l or "스포츠" in l:
        if "헬스" in s or "종합 스포츠" in s or "체력" in s:
            return "헬스장 · 피트니스 · PT"
        if "골프" in s:
            return "골프연습장 · 스크린골프"
        if any(k in s for k in ("당구", "볼링", "테니스", "탁구", "스포츠시설")):
            return "당구장 · 볼링 · 테니스 · 구기"
        if "독서실" in s or "스터디" in s or "도서관" in m:
            return "독서실 · 스터디카페"
        if "노래" in s:
            return "노래연습장 · 코인노래방"
        if "복권" in s:
            return "복권 · 로또 판매점"
        return "PC방 · 게임장 · 복합오락"

    # 5. 부동산
    if "부동산" in l:
        if any(k in nm for k in ("컨설팅", "경매", "자문", "투자", "리츠", "에셋")):
            return "부동산 컨설팅 · 경매 · 투자자문"
        if any(k in nm for k in ("관리", "임대", "개발", "디벨로퍼", "분양", "피엠", "PM", "빌딩")):
            return "부동산 임대 · 자산관리 · 분양"
        if "법인" in nm:
            return "부동산 중개법인 · 상업용중개"
        return "공인중개사사무소 (주거·상가)"

    # 6. 숙박
    if "숙박" in l:
        if "호텔" in s or "리조트" in s or "콘도" in s or "호텔" in nm:
            return "호텔 · 비즈니스호텔 · 리조트"
        if "기숙사" in s or "고시원" in s or "고시" in nm or "원룸텔" in nm or "리빙텔" in nm:
            return "고시원 · 원룸텔 · 레지던스"
        if "펜션" in s or "캠핑" in s or "글램핑" in s or "민박" in s or "게스트" in nm:
            return "펜션 · 게스트하우스 · 민박"
        return "모텔 · 일반숙박업"

    # 7. 시설관리·임대
    if "시설" in l or "임대" in l:
        if "청소" in m or "방제" in m or "소독" in s:
            return "건물청소 · 방역 · 소독 서비스"
        if "고용" in m or "인력" in s:
            return "인력공급 · 채용 · 고용알선"
        if "여행" in m or "여행" in s:
            return "여행사 · 항공/투어 예약"
        if "운송장비" in m or "자동차 대여" in s or "렌터카" in nm:
            return "렌터카 · 운송장비 대여"
        if "대여" in m or "대여" in s or "만화방" in s:
            return "생활 · 레저 · 산업장비 렌탈"
        if "시설관리" in m or "조경" in m or "유지·관리" in s:
            return "빌딩 · 사업시설 유지관리 · 조경"
        return "전시 · 행사대행 · 사무지원"

    # 8. 수리·개인
    if "수리" in l or "개인" in l:
        if "미용실" in s or "두발" in s:
            return "미용실 · 헤어살롱 · 바버샵"
        if "피부" in s:
            return "피부관리 · 에스테틱"
        if "네일" in s:
            return "네일 · 속눈썹 · 뷰티샵"
        if "자동차" in m or "정비" in s or "세차" in s:
            return "자동차 정비 · 세차 · 외장관리"
        if "세탁" in m or "빨래" in s:
            return "세탁소 · 코인빨래방"
        if "욕탕" in m or "신체관리" in m or "마사지" in s or "사우나" in s or "목욕" in s:
            return "마사지 · 체형관리 · 사우나"
        if "컴퓨터" in m or "가전제품" in m or "통신장비" in m:
            return "컴퓨터 · 휴대폰 · 가전 수리"
        if "가정용품 수리" in m or "수선" in s:
            return "의류수선 · 생활용품 수리"
        return "웨딩 · 상조 · 개인서비스 기타"

    # 9. 교육
    if "교육" in l or "학원" in l:
        if "입시" in s or "교과" in s or "일반 교육" in m:
            return "입시 · 보습 · 교과학원"
        if "요가" in s or "필라테스" in s:
            return "요가 · 필라테스 교육원"
        if "음악" in s or "미술" in s or "예술" in s:
            return "음악 · 미술 · 예체능학원"
        if "태권도" in s or "무술" in s:
            return "태권도 · 무술 · 유아체육학원"
        if "외국어" in s or "어학" in s:
            return "외국어 · 어학원"
        if "교육 지원" in m or "컨설팅" in s:
            return "유학 · 진로 · 교육컨설팅"
        return "직업훈련 · 코딩 · 자격증학원"

    # 10. 보건의료
    if "보건" in l or "의료" in l:
        if "치과" in s:
            return "치과의원 · 치과병원"
        if "한의원" in s or "한방" in s:
            return "한의원 · 한방병원"
        if "피부" in s or "성형" in s or "비뇨기" in s:
            return "피부과 · 성형외과 · 비뇨기과"
        if "외과" in s or "정형" in s:
            return "정형외과 · 외과 · 통증의원"
        if "신경" in s or "정신" in s:
            return "신경과 · 정신건강의학과"
        if "병원" in m or "병원" in s:
            return "종합병원 · 일반/요양병원"
        if "기타 보건" in m or "유사 의료" in s:
            return "심리상담 · 체형교정 · 기타보건"
        return "내과 · 소아과 · 일반의원"

    # 미분류 기타 시 중분류/소분류 실명 그대로 보존 (기타 세부 서비스 A/B 사용 금지)
    fallback_label = s or m or l or "생활밀착 전문서비스"
    return fallback_label


def get_subcategory_profile(sub_name: str, cat_large: str = "") -> Dict[str, Any]:
    """세부업종명에 해당하는 단위경제 프로파일 반환"""
    if sub_name in SUBCATEGORY_CONFIG_REGISTRY:
        return SUBCATEGORY_CONFIG_REGISTRY[sub_name]

    # 동적 생성 라벨일 경우 대분류 대표값 참조
    default_subs = LARGE_CATEGORY_DEFAULT_SUBS.get(cat_large, [])
    if default_subs:
        first_sub = default_subs[0][0]
        if first_sub in SUBCATEGORY_CONFIG_REGISTRY:
            return SUBCATEGORY_CONFIG_REGISTRY[first_sub]

    return {
        "large": cat_large or "전문서비스",
        "icon": "fa-store",
        "sales_man": 1650,
        "tx_cnt": 320,
        "card_share": 0.85,
        "visitors_per_tx": 1.25,
    }


def build_radius_sector_analytics(stores: List[Dict[str, Any]], location_factor: float = 1.0) -> Dict[str, Any]:
    """
    반경 내 실제 점포 리스트(전수)를 받아:
    - total_count
    - category_large_distribution
    - category_medium_top (정규화 세부업종 TOP)
    - card_sales_sectors (대분류 + 세부업종 계층별 점포수, 월카드매출, 결제건수, 건당단가, 업소당 일방문자 수)
    를 일괄 산출합니다.
    """
    total_count = len(stores)
    if total_count == 0:
        return {
            "total_count": 0,
            "category_large_distribution": [],
            "category_medium_top": [],
            "card_sales_sectors": [],
            "monthly_total_sales_man": 0,
            "monthly_total_count": 0,
            "avg_daily_visitors_per_store": 0.0,
        }

    loc_mult = max(0.82, min(1.28, location_factor or 1.0))

    large_counts: Dict[str, int] = {}
    sub_global_counts: Dict[str, int] = {}
    large_to_subs: Dict[str, Dict[str, int]] = {}

    for st in stores:
        c_large = (st.get("cat_large") or "전문서비스").strip()
        c_med = (st.get("cat_medium") or "").strip()
        c_sml = (st.get("cat_small") or "").strip()
        s_name = (st.get("name") or "").strip()

        sub_label = resolve_subcategory(c_large, c_med, c_sml, s_name)

        large_counts[c_large] = large_counts.get(c_large, 0) + 1
        sub_global_counts[sub_label] = sub_global_counts.get(sub_label, 0) + 1
        if c_large not in large_to_subs:
            large_to_subs[c_large] = {}
        large_to_subs[c_large][sub_label] = large_to_subs[c_large].get(sub_label, 0) + 1

    large_distribution = []
    card_sales_sectors = []
    grand_sales_man = 0
    grand_tx_cnt = 0
    grand_daily_visitors = 0.0

    for c_large, l_cnt in sorted(large_counts.items(), key=lambda x: x[1], reverse=True):
        l_ratio = round((l_cnt / total_count) * 100.0, 1)
        large_distribution.append({
            "category": c_large,
            "count": l_cnt,
            "ratio": l_ratio,
        })

        sub_map = large_to_subs.get(c_large, {})
        sub_rows = []
        sector_sales_man = 0
        sector_tx_cnt = 0
        sector_daily_visitors_total = 0.0

        for sub_name, s_cnt in sorted(sub_map.items(), key=lambda x: x[1], reverse=True):
            prof = get_subcategory_profile(sub_name, c_large)
            unit_sales = prof["sales_man"] * loc_mult
            unit_tx = prof["tx_cnt"] * loc_mult

            s_sales_man = max(10, round(s_cnt * unit_sales))
            s_tx_cnt = max(5, round(s_cnt * unit_tx))
            s_avg_pay = round((s_sales_man * 10000) / s_tx_cnt) if s_tx_cnt > 0 else 25000

            daily_per_store = calc_daily_visitors_per_store(
                tx_per_store_monthly=(s_tx_cnt / max(1, s_cnt)),
                card_share=prof["card_share"],
                visitors_per_tx=prof["visitors_per_tx"],
            )
            sub_total_daily = round(daily_per_store * s_cnt, 1)

            sector_sales_man += s_sales_man
            sector_tx_cnt += s_tx_cnt
            sector_daily_visitors_total += sub_total_daily

            sub_rows.append({
                "name": sub_name,
                "icon": prof.get("icon", "fa-tag"),
                "store_count": s_cnt,
                "store_ratio": round((s_cnt / l_cnt) * 100.0, 1) if l_cnt > 0 else 0.0,
                "monthly_sales_man": s_sales_man,
                "monthly_count": s_tx_cnt,
                "avg_payment": s_avg_pay,
                "daily_visitors_per_store": daily_per_store,
                "total_daily_visitors": round(sub_total_daily),
            })

        sector_avg_pay = round((sector_sales_man * 10000) / sector_tx_cnt) if sector_tx_cnt > 0 else 25000
        sector_daily_per_store = round(sector_daily_visitors_total / max(1, l_cnt), 1)
        top_sub_names = []
        for sr in sub_rows[:3]:
            clean_nm = sr["name"].split("(")[0].strip()
            parts = [p.strip() for p in clean_nm.split("·") if p.strip()]
            short_nm = f"{parts[0]}·{parts[1]}" if len(parts) >= 2 and len(parts[0]) <= 2 else (parts[0] if parts else clean_nm)
            top_sub_names.append(short_nm)
        sub_summary_label = " / ".join(top_sub_names) + (" 등" if len(sub_rows) > 3 else "")

        grand_sales_man += sector_sales_man
        grand_tx_cnt += sector_tx_cnt
        grand_daily_visitors += sector_daily_visitors_total

        card_sales_sectors.append({
            "category": c_large,
            "store_count": l_cnt,
            "ratio": l_ratio,
            "monthly_sales_man": sector_sales_man,
            "monthly_count": sector_tx_cnt,
            "avg_payment": sector_avg_pay,
            "daily_visitors_per_store": sector_daily_per_store,
            "total_daily_visitors": round(sector_daily_visitors_total),
            "sub_summary_label": sub_summary_label,
            "sub_categories": sub_rows,
        })

    medium_top = [
        {
            "category": s_cat,
            "count": cnt,
            "ratio": round((cnt / total_count) * 100.0, 1),
        }
        for s_cat, cnt in sorted(sub_global_counts.items(), key=lambda x: x[1], reverse=True)[:12]
    ]

    return {
        "total_count": total_count,
        "category_large_distribution": large_distribution,
        "category_medium_top": medium_top,
        "card_sales_sectors": card_sales_sectors,
        "monthly_total_sales_man": grand_sales_man,
        "monthly_total_count": grand_tx_cnt,
        "avg_daily_visitors_per_store": round(grand_daily_visitors / max(1, total_count), 1),
    }
