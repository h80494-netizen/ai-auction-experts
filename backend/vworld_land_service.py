# -*- coding: utf-8 -*-
"""
V-World 국토교통부 토지임야정보 및 토지이용계획(토지이음) 연동 서비스
- API Key: 8E5DFFF6-C1E4-48F4-83C4-0A49E53D59DE (도메인: ai-auction-experts.cloud)
- 토지특성정보(getLandCharacteristics): 지목, 토지면적, 공시지가, 용도지역, 도로접면, 지세/형상
- 토지이용계획속성(getLandUseAttr): 산업단지, 공공택지지구, 도시계획시설/도로, 개발제한구역 등 규제 및 보상 대상 분석
"""

import os
import re
import json
import logging
import requests
from typing import Dict, Any, Optional, List, Tuple

logger = logging.getLogger(__name__)

VWORLD_API_KEY = "8E5DFFF6-C1E4-48F4-83C4-0A49E53D59DE"
VWORLD_DOMAIN = "ai-auction-experts.cloud"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": f"https://{VWORLD_DOMAIN}",
    "Origin": f"https://{VWORLD_DOMAIN}"
}

# 로컬 캐시 (동일 주소/PNU 반복 호출 방지)
_LAND_CACHE: Dict[str, Dict[str, Any]] = {}


def get_pnu_from_vworld(address: str, lat: Optional[float] = None, lng: Optional[float] = None) -> Optional[str]:
    """
    V-World Geocoder API를 호출하여 주소로부터 19자리 PNU 코드를 취득합니다.
    """
    clean_addr = clean_korean_address(address)
    if not clean_addr:
        return None

    url = "https://api.vworld.kr/req/address"
    params = {
        "service": "address",
        "request": "getcoord",
        "version": "2.0",
        "crs": "EPSG:4326",
        "address": clean_addr,
        "refine": "true",
        "simple": "false",
        "format": "json",
        "type": "PARCEL",
        "key": VWORLD_API_KEY,
        "domain": VWORLD_DOMAIN
    }

    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=4)
        if resp.status_code == 200:
            data = resp.json()
            res = data.get("response", {})
            if res.get("status") == "OK":
                structure = res.get("refined", {}).get("structure", {})
                pnu = structure.get("level4LC")
                if pnu and len(pnu) == 19:
                    return pnu
    except Exception as e:
        logger.warning(f"V-World Geocoder failed for '{clean_addr}': {e}")

    # 번지 형태만 있을 때 다시 한번 시도
    m = re.search(r'([가-힣\s]+(?:시|군|구)\s+[가-힣\s]+(?:읍|면|동|리)\s*(?:산\s*)?\d+(?:-\d+)?)', clean_addr)
    if m and m.group(1) != clean_addr:
        try:
            params["address"] = m.group(1).strip()
            resp = requests.get(url, params=params, headers=HEADERS, timeout=4)
            if resp.status_code == 200:
                data = resp.json()
                res = data.get("response", {})
                if res.get("status") == "OK":
                    structure = res.get("refined", {}).get("structure", {})
                    pnu = structure.get("level4LC")
                    if pnu and len(pnu) == 19:
                        return pnu
        except Exception:
            pass

    return None


def clean_korean_address(addr: str) -> str:
    """주소에서 괄호, 호수, 층수 등을 제거하고 순수 지번 주소로 정제"""
    if not addr:
        return ""
    text = re.sub(r'\[.*?\]|\(.*?\)', ' ', addr)
    text = re.sub(r'\b\d+층.*|\b\d+호.*', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def fetch_vworld_land_characteristics(pnu: str) -> Optional[Dict[str, Any]]:
    """
    V-World 토지특성정보조회 (getLandCharacteristics)
    실측 지목, 토지면적, 공시지가, 용도지역1/2 반환
    """
    if not pnu or len(pnu) != 19:
        return None

    url = "http://api.vworld.kr/ned/data/getLandCharacteristics"
    params = {
        "key": VWORLD_API_KEY,
        "domain": VWORLD_DOMAIN,
        "pnu": pnu,
        "format": "json",
        "numOfRows": "5",
        "pageNo": "1"
    }

    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            container = data.get("landCharacteristicss", {}) or data.get("response", {})
            fields = container.get("field", [])
            if isinstance(fields, list) and len(fields) > 0:
                # 최신 연도순 정렬
                sorted_fields = sorted(fields, key=lambda x: str(x.get("stdrYear", "")), reverse=True)
                latest = sorted_fields[0]
                
                # 지목명, 면적, 공시지가, 용도지역명 추출
                jimok = latest.get("lndcgrCodeNm") or ""
                area_sqm = float(latest.get("lndpclAr") or 0.0)
                official_price = float(latest.get("pblntfPclnd") or 0.0)
                zoning1 = latest.get("prposArea1Nm") or ""
                zoning2 = latest.get("prposArea2Nm") or ""
                road_side = latest.get("roadSideCodeNm") or ""
                height = latest.get("tpgrphHgCodeNm") or ""
                shape = latest.get("tpgrphFrmCodeNm") or ""
                stdr_year = latest.get("stdrYear") or ""

                return {
                    "source": "vworld_characteristics",
                    "pnu": pnu,
                    "stdr_year": stdr_year,
                    "jimok": jimok,
                    "area_sqm": area_sqm,
                    "official_price_sqm": official_price,
                    "zoning": zoning1 if zoning1 and zoning1 != "-" else zoning2,
                    "zoning1": zoning1,
                    "zoning2": zoning2,
                    "road_side": road_side,
                    "height": height,
                    "shape": shape
                }
    except Exception as e:
        logger.warning(f"V-World getLandCharacteristics failed for PNU {pnu}: {e}")

    return None


def fetch_vworld_land_use_attr(pnu: str) -> Optional[Dict[str, Any]]:
    """
    V-World 토지이용계획속성조회 (getLandUseAttr - 토지이음)
    용도지역지구구역 목록 및 산업단지/공공택지/도시계획시설 분류
    """
    if not pnu or len(pnu) != 19:
        return None

    url = "http://api.vworld.kr/ned/data/getLandUseAttr"
    params = {
        "key": VWORLD_API_KEY,
        "domain": VWORLD_DOMAIN,
        "pnu": pnu,
        "format": "json",
        "numOfRows": "50",
        "pageNo": "1"
    }

    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            container = data.get("landUses", {})
            fields = container.get("field", [])
            if isinstance(fields, list) and len(fields) > 0:
                raw_zones = []
                zonings = []
                industrial_zones = []
                public_housing_zones = []
                urban_facilities = []
                deregulation_zones = []
                green_belts = []

                for item in fields:
                    zone_name = (item.get("prposAreaDstrcCodeNm") or "").strip()
                    cnflc = (item.get("cnflcAtNm") or "").strip() # 저촉, 포함 등
                    if not zone_name or zone_name in raw_zones:
                        continue
                    raw_zones.append(zone_name)

                    # 1. 국토계획법상 21개 표준 용도지역 필터
                    STANDARD_ZONINGS = [
                        "제1종전용주거지역", "제2종전용주거지역", "제1종일반주거지역", "제2종일반주거지역", "제3종일반주거지역", "준주거지역",
                        "중심상업지역", "일반상업지역", "근린상업지역", "유통상업지역",
                        "전용공업지역", "일반공업지역", "준공업지역",
                        "보전녹지지역", "생산녹지지역", "자연녹지지역",
                        "보전관리지역", "생산관리지역", "계획관리지역",
                        "농림지역", "자연환경보전지역"
                    ]
                    for std_z in STANDARD_ZONINGS:
                        if std_z in zone_name:
                            if std_z not in zonings:
                                zonings.append(std_z)
                            break

                    # 2. 산업단지 관련
                    if any(k in zone_name for k in ["산업단지", "국가산단", "일반산단", "도시첨단산업단지", "지식산업", "공장입지", "농공단지"]):
                        industrial_zones.append({"name": zone_name, "status": cnflc or "지정"})

                    # 3. 공공택지지구 / 공공주택지구 / 도시개발구역
                    if any(k in zone_name for k in ["공공주택지구", "택지개발", "도시개발구역", "재정비촉진", "보금자리", "주거환경개선"]):
                        public_housing_zones.append({"name": zone_name, "status": cnflc or "지정"})

                    # 4. 도시계획시설 / 도시기반시설 (도로, 철도, 공원, 완충녹지 등)
                    is_zoning_name = any(zone_name.endswith(zn) for zn in ["녹지지역", "주거지역", "상업지역", "공업지역", "관리지역", "농림지역", "보전지역"])
                    if not is_zoning_name and any(k in zone_name for k in ["도로", "철도", "공원", "완충녹지", "경관녹지", "연결녹지", "광장", "유수지", "하천", "공공공지", "학교", "주차장", "도시계획시설"]):
                        urban_facilities.append({"name": zone_name, "status": cnflc or "지정"})

                    # 5. 개발제한구역 (그린벨트)
                    if "개발제한구역" in zone_name:
                        green_belts.append(zone_name)

                    # 6. 기타 규제완화/지구단위
                    if "지구단위계획" in zone_name:
                        deregulation_zones.append(zone_name)

                primary_zoning = zonings[0] if zonings else None

                return {
                    "source": "vworld_land_use",
                    "pnu": pnu,
                    "all_zones": raw_zones,
                    "primary_zoning": primary_zoning,
                    "zonings": zonings,
                    "industrial_zones": industrial_zones,
                    "public_housing_zones": public_housing_zones,
                    "urban_facilities": urban_facilities,
                    "green_belts": green_belts,
                    "deregulation_zones": deregulation_zones,
                    "is_compensation_target": bool(industrial_zones or public_housing_zones or urban_facilities)
                }
    except Exception as e:
        logger.warning(f"V-World getLandUseAttr failed for PNU {pnu}: {e}")

    return None


_EUM_SESSION: Optional[requests.Session] = None
_EUM_LOGIN_ATTEMPTED: bool = False
_EUM_GOSI_CACHE: Dict[str, List[Dict[str, str]]] = {}


def _get_eum_session() -> requests.Session:
    """
    국토교통부 토지이음(eum.go.kr) 세션을 생성하고 계정(h80494) 로그인 연동을 1회 시도합니다.
    (비밀번호 5회 오류 잠금 방지를 위해 프로세스당 최대 1회만 로그인 시도하며,
     토지이용계획 열람 및 고시정보는 세션 쿠키 기반으로 즉시 조회합니다.)
    """
    global _EUM_SESSION, _EUM_LOGIN_ATTEMPTED
    if _EUM_SESSION is not None:
        return _EUM_SESSION

    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.eum.go.kr/web/am/amMain.jsp"
    })
    if not _EUM_LOGIN_ATTEMPTED:
        _EUM_LOGIN_ATTEMPTED = True
        login_id = os.getenv("EUM_LOGIN_ID", "h80494")
        login_pw = os.getenv("EUM_LOGIN_PW", "spring11!!")
        try:
            r_init = s.get("https://www.eum.go.kr/web/mb/mbLogin.jsp", timeout=4)
            m_csrf = re.search(r'name="_csrf"\s+value="([^"]+)"', r_init.text)
            if m_csrf and login_id and login_pw:
                csrf_token = m_csrf.group(1)
                s.post(
                    "https://www.eum.go.kr/web/mb/mbLoginAjaxXml.jsp",
                    data={
                        "function": "selectLogin",
                        "loginId": login_id,
                        "pswd": login_pw,
                        "_csrf": csrf_token
                    },
                    headers={
                        "X-CSRF-TOKEN": csrf_token,
                        "X-Requested-With": "XMLHttpRequest",
                        "Referer": "https://www.eum.go.kr/web/mb/mbLogin.jsp"
                    },
                    timeout=4
                )
        except Exception as e:
            logger.debug(f"EUM session init note: {e}")

    _EUM_SESSION = s
    return s


def fetch_eum_direct_land_and_gosi(pnu: str) -> Dict[str, Any]:
    """
    토지이음(eum.go.kr) 필지별 토지이용계획 열람(luLandDet.jsp) 및
    관할 시·군·구 최신 고시·공람(gvGosiList.jsp) 원문을 실시간 조회합니다.
    - 개발행위허가제한지역, 토지거래허가구역(지정기간·용도), 지구단위계획, 도시계획시설, 정비구역 등 추출
    """
    result: Dict[str, Any] = {
        "mark1_zones": [],
        "mark2_zones": [],
        "mark3_notes": [],
        "permit_restriction_zones": [],
        "land_tx_permit_zones": [],
        "recent_gosi_list": [],
        "jimok": None,
        "area_sqm": None
    }
    if not pnu or len(pnu) != 19:
        return result

    s = _get_eum_session()

    # 1. 필지별 토지이용계획 및 추가기재(개발행위허가제한지역·토지거래허가구역 등) 파싱
    try:
        r_det = s.get(
            "https://www.eum.go.kr/web/ar/lu/luLandDet.jsp",
            params={"pnu": pnu, "mode": "search", "isNoScr": "script"},
            timeout=5
        )
        if r_det.status_code == 200 and r_det.text:
            html_text = r_det.text

            m_jm = re.search(r'id="present_class_val"\s+value="([^"]+)"', html_text)
            if m_jm:
                result["jimok"] = m_jm.group(1).strip()

            m_ar = re.search(r'<td[^>]*id="present_area"[^>]*>([^<]+)</td>', html_text)
            if m_ar:
                ar_str = re.sub(r'[^0-9.]', '', m_ar.group(1))
                if ar_str:
                    result["area_sqm"] = float(ar_str)

            def _extract_td_clean(td_id: str) -> str:
                m_td = re.search(rf'<td[^>]*id="{td_id}"[^>]*>(.*?)</td>', html_text, re.S)
                if not m_td:
                    return ""
                raw_inner = re.sub(r'<div[^>]*class="layer_pop.*?</div>\s*</div>\s*</div>\s*</div>', ' ', m_td.group(1), flags=re.S)
                raw_inner = re.sub(r'<[^>]+>', ' ', raw_inner)
                raw_inner = raw_inner.replace('&lt;', '<').replace('&gt;', '>').replace('&nbsp;', ' ')
                return re.sub(r'\s+', ' ', raw_inner).strip()

            mark1_str = _extract_td_clean("present_mark1")
            mark2_str = _extract_td_clean("present_mark2")
            mark3_str = _extract_td_clean("present_mark3")

            if mark1_str:
                result["mark1_zones"] = [z.strip() for z in mark1_str.split(",") if z.strip()]
            if mark2_str:
                result["mark2_zones"] = [z.strip() for z in mark2_str.split(",") if z.strip()]
            if mark3_str:
                result["mark3_notes"] = [z.strip() for z in re.split(r'\)\s*,|,\s*(?=토지거래|개발행위)', mark3_str) if z.strip()]

            combined_items = result["mark1_zones"] + result["mark2_zones"] + result["mark3_notes"]
            for item in combined_items:
                if any(k in item for k in ["개발행위허가제한", "개발행위제한", "행위제한"]):
                    if item not in result["permit_restriction_zones"]:
                        result["permit_restriction_zones"].append(item)
                if "토지거래계약에관한허가구역" in item or "토지거래허가" in item:
                    if item not in result["land_tx_permit_zones"]:
                        result["land_tx_permit_zones"].append(item)
    except Exception as e:
        logger.warning(f"EUM luLandDet fetch failed for PNU {pnu}: {e}")

    # 2. 관할 시·군·구(pnu[:5]) 토지이음 최신 고시·공람(gvGosiList.jsp) 조회 (캐시 적용)
    sgg_cd = pnu[:5]
    if sgg_cd in _EUM_GOSI_CACHE:
        result["recent_gosi_list"] = _EUM_GOSI_CACHE[sgg_cd]
    else:
        try:
            r_gosi = s.get(
                "https://www.eum.go.kr/web/gs/gv/gvGosiList.jsp",
                params={"selSggCd": sgg_cd},
                timeout=4
            )
            if r_gosi.status_code == 200 and r_gosi.text:
                gosi_items: List[Dict[str, str]] = []
                rows = re.findall(r'<tr[^>]*>(.*?)</tr>', r_gosi.text, re.S)
                for row_html in rows[1:8]:
                    tds = re.findall(r'<td[^>]*>(.*?)</td>', row_html, re.S)
                    if len(tds) >= 4:
                        clean_tds = [re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', c)).strip() for c in tds]
                        if clean_tds[0] and re.match(r'\d{4}[-.]\d{2}[-.]\d{2}', clean_tds[0]):
                            gosi_items.append({
                                "date": clean_tds[0],
                                "gosi_no": clean_tds[1],
                                "title": clean_tds[2],
                                "org": clean_tds[3]
                            })
                _EUM_GOSI_CACHE[sgg_cd] = gosi_items[:5]
                result["recent_gosi_list"] = _EUM_GOSI_CACHE[sgg_cd]
        except Exception as e:
            logger.warning(f"EUM gvGosiList fetch failed for SGG {sgg_cd}: {e}")

    return result


def get_comprehensive_land_info(address: str, lat: Optional[float] = None, lng: Optional[float] = None) -> Dict[str, Any]:
    """
    주소 및 좌표를 바탕으로 V-World 토지특성, 토지이용계획 및 토지이음(eum.go.kr) 원문을 종합 조회하여
    정확한 용도지역, 지목, 면적, 공시지가, 개발행위허가제한지역·토지보상 대상 여부를 반환합니다.
    """
    cache_key = f"{address}_{lat}_{lng}"
    if cache_key in _LAND_CACHE:
        return _LAND_CACHE[cache_key]

    pnu = get_pnu_from_vworld(address, lat, lng)
    char_info = None
    use_info = None
    eum_info: Dict[str, Any] = {}

    if pnu:
        char_info = fetch_vworld_land_characteristics(pnu)
        use_info = fetch_vworld_land_use_attr(pnu)
        eum_info = fetch_eum_direct_land_and_gosi(pnu)

    if use_info is None:
        use_info = {
            "source": "eum_direct",
            "pnu": pnu,
            "all_zones": [],
            "primary_zoning": None,
            "zonings": [],
            "industrial_zones": [],
            "public_housing_zones": [],
            "urban_facilities": [],
            "green_belts": [],
            "deregulation_zones": [],
            "is_compensation_target": False
        }

    # 토지이음 실시간 파싱 데이터 병합
    if eum_info:
        for z in (eum_info.get("mark1_zones", []) + eum_info.get("mark2_zones", [])):
            clean_z = re.sub(r'<[^>]+>', '', z).strip()
            if clean_z and clean_z not in use_info["all_zones"]:
                use_info["all_zones"].append(clean_z)
        use_info["permit_restriction_zones"] = eum_info.get("permit_restriction_zones", [])
        use_info["land_tx_permit_zones"] = eum_info.get("land_tx_permit_zones", [])
        use_info["mark3_notes"] = eum_info.get("mark3_notes", [])
        use_info["recent_gosi_list"] = eum_info.get("recent_gosi_list", [])
        if use_info["permit_restriction_zones"]:
            use_info["is_compensation_target"] = True

    # 지목 판별
    jimok = None
    if char_info and char_info.get("jimok"):
        jimok = char_info["jimok"]
    elif eum_info and eum_info.get("jimok"):
        jimok = eum_info["jimok"]

    # 용도지역 판별 (토지이용계획 우선 > 토지특성 > None)
    zoning = None
    if use_info and use_info.get("primary_zoning"):
        zoning = use_info["primary_zoning"]
    elif char_info and char_info.get("zoning"):
        zoning = char_info["zoning"]

    # 토지면적 (㎡)
    area_sqm = None
    if char_info and char_info.get("area_sqm"):
        area_sqm = char_info["area_sqm"]
    elif eum_info and eum_info.get("area_sqm"):
        area_sqm = eum_info["area_sqm"]

    # 공시지가 (원/㎡)
    official_price_sqm = None
    if char_info and char_info.get("official_price_sqm"):
        official_price_sqm = char_info["official_price_sqm"]

    result = {
        "status": "success" if (char_info or use_info or eum_info) else "partial",
        "pnu": pnu,
        "jimok": jimok,
        "zoning": zoning,
        "area_sqm": area_sqm,
        "official_price_sqm": official_price_sqm,
        "char_info": char_info or {},
        "use_info": use_info or {},
        "eum_info": eum_info or {}
    }

    _LAND_CACHE[cache_key] = result
    return result
