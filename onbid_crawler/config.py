import os
import urllib.parse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 동적 설정 레지스트리 (환경변수 우선 참조)
ONBID_CONFIG = {
    # 인증키 설정 (기존 목록 조회키 및 신규 입찰결과 상세 조회키)
    "rlst_list_service_key": urllib.parse.unquote(
        os.environ.get(
            "ONBID_RLST_LIST_KEY",
            "876c80d2a9fd79ade2c9c2fea0d0d1b0657c4b4aadfc4917065326b6e7fa32b6",
        )
    ),
    "bid_rslt_service_key": urllib.parse.unquote(
        os.environ.get(
            "ONBID_BID_RSLT_KEY",
            "R6zpn4dzyzuasYP5k7dxF1K%2Bgv1J4nes6bhZCrVeZYkPlm%2B%2Blz96SoaeBLlLvpqjsKyST6S0mmVtEa5zRctGng%3D%3D",
        )
    ),
    # API 엔드포인트
    "rlst_list_url": "https://apis.data.go.kr/B010003/OnbidRlstListSrvc2/getRlstCltrList2",
    "bid_rslt_dtl_url": "https://apis.data.go.kr/B010003/OnbidCltrBidRsltDtlSrvc2/getCltrBidRsltDtl2",
    "bid_rslt_list_url": "https://apis.data.go.kr/B010003/OnbidCltrBidRsltListSrvc2/getCltrBidRsltList2",
    # 조회 대상 지역 및 재산유형 코드
    "target_regions": ["서울특별시", "경기도", "인천광역시", "강원특별자치도", "충청남도", "전남"],
    "prpt_div_cd": "0007,0010,0005,0004,0002,0003,0006,0008,0011,0013",
    # 입찰결과 상태 코드 매핑 (api_guide.txt 명세 기준)
    "pbct_stat_codes": {
        "0001": "입찰준비중",
        "0002": "입찰진행중",
        "0003": "입찰마감",
        "0006": "개찰중",
        "0009": "수의계약가능",
        "0010": "낙찰",
        "0011": "유찰",
        "0012": "취소",
    },
    # 일일 트래픽(1,000건) 보호를 위한 1회 실행당 최대 상세 API 호출 수 및 캐시 경로
    "max_dtl_calls_per_run": int(os.environ.get("ONBID_MAX_DTL_CALLS", "800")),
    "cache_filepath": os.path.join(BASE_DIR, "onbid_rslt_cache.json"),
}

