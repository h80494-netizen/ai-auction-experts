import os
import sys
import glob
import json
import math
import time
import shutil
import sqlite3
import subprocess
import argparse
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import pandas as pd
import openpyxl

# 디렉토리 및 파일 경로 설정
ONBID_DIR = os.path.dirname(os.path.abspath(__file__))
DOOIN_ROOT = os.path.dirname(ONBID_DIR)
VIBECODING_DIR = os.path.join(DOOIN_ROOT, "바이브코딩")
UPDATE_DIR = os.path.join(VIBECODING_DIR, "data", "경공매업데이트")
FINAL_EXCEL_PATH = os.path.join(UPDATE_DIR, "경공매데이터_업데이트_대항력추가.xlsx")
WORKBOOK_1_PATH = os.path.join(DOOIN_ROOT, "두인경매_작업파일_1.xlsm")
RAWDATA_FIXED_PATH = os.path.join(DOOIN_ROOT, "두인경공매_rawdata261109.xlsx")
REF_JSON_PATH = os.path.join(ONBID_DIR, "weekly_reference_data.json")
LOG_DIR = os.path.join(ONBID_DIR, "logs")

# 엑셀 KakaoGeocode UDF에 설정된 동일한 Kakao REST API 키
KAKAO_REST_API_KEY = os.environ.get("KAKAO_REST_API_KEY", "9e5265220f87e54e4379077cb60071bb")


def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = os.path.join(LOG_DIR, f"weekly_pipeline_{datetime.now().strftime('%Y%m%d')}.log")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def get_latest_file(folder: str, pattern: str, exclude_keyword: str = "요약") -> str:
    search_path = os.path.join(folder, pattern)
    files = [
        f for f in glob.glob(search_path)
        if (not exclude_keyword or exclude_keyword not in os.path.basename(f))
        and not os.path.basename(f).startswith("~$")
    ]
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0] if files else ""


def run_step1_crawlers():
    """1단계: 온비드 공매 + 두인경매(수도권 + 충남·강원·전남) 크롤링 순차 실행"""
    log("=" * 70)
    log("1단계: 온비드 공매 및 두인경매(수도권+강원·충남·전남) 자동 크롤링 시작")
    log("=" * 70)

    scripts = [
        ("온비드 공매 크롤링", "onbid_crawler.py"),
        ("두인경매 수도권(인천·서울·경기) 크롤링", "run_dooin_merged.py"),
        ("두인경매 지방권(강원·충남·전남) 크롤링", "run_dooin_regional_merged.py"),
    ]
    for label, script_name in scripts:
        script_path = os.path.join(ONBID_DIR, script_name)
        log(f"▶ {label} 실행 중: {script_path}")
        res = subprocess.run([sys.executable, script_path], cwd=ONBID_DIR)
        if res.returncode != 0:
            log(f"⚠️ [경고] {script_name} 종료 코드: {res.returncode} (최신 생성 파일로 계속 진행합니다)")
        else:
            log(f"✅ {label} 완료")


def clean_address_for_geocode(addr: str) -> str:
    """엑셀 주소 문자열에서 지오코딩 정확도를 높이기 위해 불필요한 외 필지/호수 꼬리표를 정리"""
    if not addr:
        return ""
    s = str(addr).strip()
    # 괄호 안 내용 및 '외 X필지' 제거한 보조 검색어도 함께 활용 가능하도록 원문 정리
    s = re.sub(r"\s+", " ", s)
    return s


def kakao_geocode_single(address: str) -> tuple:
    """
    엑셀 KakaoGeocode(주소, API_KEY, "경도"/"위도") VBA 함수와 100% 동일한
    Kakao Local REST API를 호출하여 (경도, 위도)를 반환합니다.
    """
    addr_clean = clean_address_for_geocode(address)
    if not addr_clean:
        return (0.0, 0.0)

    headers = {"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"}

    # 검색 후보 생성: 1) 원문, 2) '외 N필지' 및 상세 동·호수 제거 지번 주소
    candidates = [addr_clean]
    short_addr = re.sub(r"\s*외\s*\d+\s*필지.*", "", addr_clean)
    short_addr = re.sub(r"\([^)]*\)", "", short_addr).strip()
    if "," in short_addr:
        short_addr = short_addr.split(",")[0].strip()
    if short_addr and short_addr not in candidates:
        candidates.append(short_addr)

    # 지번까지만 추출한 후보
    m_jibun = re.match(r"^([가-힣]+(?:특별시|광역시|특별자치시|도|특별자치도)?\s+[가-힣0-9]+(?:시|군|구)\s+[가-힣0-9\s]+(?:읍|면|동|가|리|로|길)\s*(?:산?\s*\d+(?:-\d+)?))", short_addr)
    if m_jibun:
        jb = m_jibun.group(1).strip()
        if jb not in candidates:
            candidates.append(jb)

    for q in candidates:
        try:
            resp = requests.get(
                "https://dapi.kakao.com/v2/local/search/address.json",
                headers=headers,
                params={"query": q, "size": 1},
                timeout=5,
            )
            if resp.status_code == 200:
                docs = resp.json().get("documents") or []
                if docs:
                    lng = float(docs[0].get("x") or 0.0)
                    lat = float(docs[0].get("y") or 0.0)
                    if lng > 120 and lat > 30:
                        return (lng, lat)
        except Exception:
            pass

        try:
            resp_kw = requests.get(
                "https://dapi.kakao.com/v2/local/search/keyword.json",
                headers=headers,
                params={"query": q, "size": 1},
                timeout=5,
            )
            if resp_kw.status_code == 200:
                docs = resp_kw.json().get("documents") or []
                if docs:
                    lng = float(docs[0].get("x") or 0.0)
                    lat = float(docs[0].get("y") or 0.0)
                    if lng > 120 and lat > 30:
                        return (lng, lat)
        except Exception:
            pass

    return (0.0, 0.0)


def parse_dooin_raw_to_refined(df_merged: pd.DataFrame) -> pd.DataFrame:
    """
    두인경매_작업파일_1.xlsm의 [Sheet4] 및 [전체1] 수식과 100% 동일한 규칙으로
    [통합] 시트 원본 데이터를 14개 표준 경매 컬럼으로 변환합니다.
    """
    records = []
    for _, row in df_merged.iterrows():
        raw_sano = str(row.get("saNo") or "").strip()
        clean_text = raw_sano.split("<")[0].strip() if "<" in raw_sano else raw_sano
        sano_formatted = clean_text.replace("-", " 타경 ")
        m_sub = re.search(r"\(([^)]+)\)", raw_sano)
        if m_sub:
            sano_formatted = f"{sano_formatted}({m_sub.group(1)})"

        ctgr = str(row.get("ctgr") or "").strip()
        addr = str(row.get("regnAdrs") or row.get("adrsInfo") or "").strip()
        raw_area = str(row.get("areaInfo") or "")

        has_bldg = "건물" in raw_area
        land_kw = "대지권" if "대지권" in raw_area else "토지"
        has_land = land_kw in raw_area

        bldg_py_str = ""
        bldg_py_val = 0.0
        if has_bldg:
            after_b = raw_area.split("건물", 1)[1]
            if "평)" in after_b and "(" in after_b.split("평)", 1)[0]:
                bldg_py_str = after_b.split("평)", 1)[0].split("(")[-1].strip()
                try:
                    bldg_py_val = float(bldg_py_str.replace(",", ""))
                except Exception:
                    bldg_py_val = 0.0

        land_py_str = ""
        land_py_val = 0.0
        if has_land:
            after_l = raw_area.split(land_kw, 1)[1]
            if "평)" in after_l and "(" in after_l.split("평)", 1)[0]:
                land_py_str = after_l.split("평)", 1)[0].split("(")[-1].strip()
                try:
                    land_py_val = float(land_py_str.replace(",", ""))
                except Exception:
                    land_py_val = 0.0

        if has_bldg:
            basic_str = f"건물 {bldg_py_str}평, 토지 {land_py_str}평"
        else:
            basic_str = f"토지 {land_py_str}평"

        spl_cdtn = str(row.get("splCdtn") or "").strip()
        if spl_cdtn == "nan":
            spl_cdtn = ""

        apsl_amt = row.get("apslAmt")
        minb_amt = row.get("minbAmt")
        bid_dt = str(row.get("bidDt") or "").strip()
        stat_nm = str(row.get("statNm") or "").strip()
        try:
            minb_pct = float(str(row.get("minbPct") or "0").replace(",", "")) / 100.0
        except Exception:
            minb_pct = 0.0
        hit = row.get("hit")

        records.append({
            "해당법원": 1,
            "사건번호": sano_formatted,
            "종류": ctgr,
            "주소": addr,
            "기본": basic_str,
            "전용면적(평)": bldg_py_val if has_bldg else 0.0,
            "대지권(평)": land_py_val,
            "특이사항": spl_cdtn if spl_cdtn else "0",
            "감정가": apsl_amt,
            "최저가": minb_amt,
            "입찰일": bid_dt,
            "입찰상황": stat_nm,
            "낙찰율": minb_pct,
            "조회수": hit,
        })
    return pd.DataFrame(records)


def load_existing_cache() -> dict:
    """
    기존 경공매데이터_업데이트_대항력추가.xlsx에서
    사건번호 및 주소별 기산출 (경도, 위도) 및 공간지표(29~45번 컬럼) 캐시를 로드합니다.
    """
    cache_by_case = {}
    cache_by_addr = {}
    if not os.path.exists(FINAL_EXCEL_PATH):
        return {"by_case": cache_by_case, "by_addr": cache_by_addr}

    log(f"기존 마스터 엑셀에서 좌표/공간지표 캐시 로드 중: {FINAL_EXCEL_PATH}")
    df_prev = pd.read_excel(FINAL_EXCEL_PATH)
    spatial_cols = [
        "전철역", "노선", "역거리", "더블역세권", "GTX 거리", "GTX역사",
        "중학교", "반경", "산단", "산단거리", "대학명", "대학거리",
        "세대수", "IC명", "IC거리", "경도", "위도"
    ]
    for row in df_prev.to_dict("records"):
        try:
            lng = float(row.get("경도") or 0.0)
            lat = float(row.get("위도") or 0.0)
        except Exception:
            continue
        if lng <= 120 or lat <= 30:
            continue

        entry = {c: row.get(c) for c in spatial_cols}
        cno = str(row.get("사건번호") or "").replace(" ", "").strip()
        addr = str(row.get("주소") or "").strip()
        if cno:
            cache_by_case[cno] = entry
        if addr:
            cache_by_addr[addr] = entry

    log(f"  -> 캐시 로드 완료: 사건번호 기준 {len(cache_by_case):,}건, 주소 기준 {len(cache_by_addr):,}건")
    return {"by_case": cache_by_case, "by_addr": cache_by_addr}


def haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def compute_spatial_features_for_coord(lat: float, lng: float, ref: dict) -> dict:
    """신규 지오코딩된 (위도, 경도)에 대해 최근접 역세권, GTX, 중학교, 산단, 대학, IC 거리를 산출"""
    res = {
        "전철역": "0",
        "노선": "0",
        "역거리": 99999.0,
        "더블역세권": 0,
        "GTX 거리": 99999.0,
        "GTX역사": "0",
        "중학교": "0",
        "반경": 99999.0,
        "산단": "0",
        "산단거리": 99999.0,
        "대학명": "0",
        "대학거리": 99999.0,
        "세대수": 0,
        "IC명": "0",
        "IC거리": 99999.0,
        "경도": lng,
        "위도": lat,
    }
    if lat <= 30 or lng <= 120:
        return res

    # 1. 지하철역 & GTX
    subways = ref.get("subways") or []
    station_lines = ref.get("station_lines") or {}
    best_sub_dist = 999999.0
    best_sub_name = "0"
    best_gtx_dist = 999999.0
    best_gtx_line = "0"

    for s in subways:
        d = haversine_m(lat, lng, s["lat"], s["lng"])
        ln = s.get("line", "")
        if "GTX" in ln.upper():
            if d < best_gtx_dist:
                best_gtx_dist = d
                best_gtx_line = ln
        if d < best_sub_dist:
            best_sub_dist = d
            best_sub_name = s["name"]

    if best_sub_name != "0":
        lines = station_lines.get(best_sub_name) or []
        res["전철역"] = best_sub_name
        res["노선"] = ",".join(lines) if lines else "수도권전철"
        res["역거리"] = best_sub_dist
        res["더블역세권"] = len(lines) if lines else 1

    if best_gtx_dist < 999999.0:
        res["GTX 거리"] = best_gtx_dist
        res["GTX역사"] = best_gtx_line if best_gtx_dist <= 5000 else "0"

    # 2. 중학교
    best_ms_dist = 999999.0
    best_ms_name = "0"
    for m in (ref.get("middle_schools") or []):
        d = haversine_m(lat, lng, m["lat"], m["lng"])
        if d < best_ms_dist:
            best_ms_dist = d
            best_ms_name = m["name"]
    if best_ms_name != "0":
        res["중학교"] = best_ms_name
        res["반경"] = best_ms_dist

    # 3. 산단
    best_ind_dist = 999999.0
    best_ind_name = "0"
    for ind in (ref.get("industrial_parks") or []):
        d = haversine_m(lat, lng, ind["lat"], ind["lng"])
        if d < best_ind_dist:
            best_ind_dist = d
            best_ind_name = ind["name"]
    if best_ind_name != "0":
        res["산단"] = best_ind_name
        res["산단거리"] = best_ind_dist

    # 4. 대학
    best_u_dist = 999999.0
    best_u_name = "0"
    for u in (ref.get("universities") or []):
        d = haversine_m(lat, lng, u["lat"], u["lng"])
        if d < best_u_dist:
            best_u_dist = d
            best_u_name = u["name"]
    if best_u_name != "0":
        res["대학명"] = best_u_name
        res["대학거리"] = best_u_dist

    # 5. IC(톨게이트)
    best_ic_dist = 999999.0
    best_ic_name = "0"
    for ic in (ref.get("tollgates") or []):
        d = haversine_m(lat, lng, ic["lat"], ic["lng"])
        if d < best_ic_dist:
            best_ic_dist = d
            best_ic_name = ic["name"]
    if best_ic_name != "0":
        res["IC명"] = best_ic_name
        res["IC거리"] = best_ic_dist

    return res


def update_workbooks_and_build_master(
    onbid_excel: str,
    sudo_excel: str,
    regional_excel: str,
):
    """
    2~4단계:
    - 두인경매_작업파일_1.xlsm의 맨 끝 시트([통합]) 업데이트
    - 두인경공매_rawdata의 [관심1] 및 [경매종합] 시트 업데이트
    - 신규 물건만 KakaoGeocode로 경도·위도 산출
    - 경공매업데이트 폴더에 최종 45개 컬럼 마스터 파일(경공매데이터_업데이트_대항력추가.xlsx) 생성
    """
    log("=" * 70)
    log("2단계: 크롤링 데이터 병합 및 작업 엑셀 시트 업데이트 시작")
    log("=" * 70)

    df_onbid = pd.read_excel(onbid_excel)
    df_sudo = pd.read_excel(sudo_excel)
    df_reg = pd.read_excel(regional_excel)
    df_auction_raw = pd.concat([df_sudo, df_reg], ignore_index=True)
    if "tid" in df_auction_raw.columns:
        df_auction_raw = df_auction_raw.drop_duplicates(subset=["tid"], keep="first").reset_index(drop=True)

    log(f"  - 온비드 공매 수집 건수: {len(df_onbid):,}건 ({os.path.basename(onbid_excel)})")
    log(f"  - 두인경매 통합(수도권+강원·충남·전남) 건수: {len(df_auction_raw):,}건")

    # 경매 정제 데이터 생성 ([Sheet4] / [전체1] 동일 로직)
    df_auction_refined = parse_dooin_raw_to_refined(df_auction_raw)

    # 기존 좌표 캐시 로드
    cache = load_existing_cache()
    by_case = cache["by_case"]
    by_addr = cache["by_addr"]

    # 레퍼런스 테이블 로드
    ref = {}
    if os.path.exists(REF_JSON_PATH):
        with open(REF_JSON_PATH, "r", encoding="utf-8") as f:
            ref = json.load(f)

    # 공매 표준 행 변환 ([관심1] -> [관심종목] -> [공매] 수식 동일 적용)
    gongmae_rows = []
    for _, r in df_onbid.iterrows():
        cno = str(r.get("물건관리번호") or "").strip()
        if not cno or cno == "nan":
            continue
        usg = str(r.get("용도") or "").strip()
        raw_addr = str(r.get("물건명") or r.get("소재지") or "").strip()
        addr = (
            raw_addr.replace("경기도", "경기")
            .replace("서울특별시", "서울")
            .replace("인천광역시", "인천")
            .replace("충청남도", "충남")
            .replace("강원특별자치도", "강원")
            .replace("강원도", "강원")
            .replace("전라남도", "전남")
            .replace("제주특별자치도", "제주")
        )
        try:
            land_sqm = float(str(r.get("토지면적(㎡)") or "0").replace(",", ""))
        except Exception:
            land_sqm = 0.0
        try:
            bldg_sqm = float(str(r.get("건물면적(㎡)") or "0").replace(",", ""))
        except Exception:
            bldg_sqm = 0.0

        bldg_py = bldg_sqm / 3.3 if bldg_sqm > 0 else 0.0
        land_py = land_sqm / 3.3 if land_sqm > 0 else 0.0
        if bldg_py == 0:
            basic_str = f"0평 / {land_py:,.1f}평"
        elif land_py == 0:
            basic_str = f"{bldg_py:,.1f}평"
        else:
            basic_str = f"{bldg_py:,.1f}평 / {land_py:,.1f}평"

        stat_str = str(r.get("물건상태") or "").strip()
        cancel_reason = str(r.get("취소/회수사유") or "").strip()
        if cancel_reason and cancel_reason != "nan":
            stat_str = f"{stat_str} ({cancel_reason})" if stat_str else cancel_reason

        try:
            apsl_val = float(str(r.get("감정가(원)") or "0").replace(",", ""))
        except Exception:
            apsl_val = 0.0
        try:
            min_val = float(str(r.get("최저입찰가(원)") or "0").replace(",", ""))
        except Exception:
            min_val = apsl_val
        if min_val <= 0 and apsl_val > 0:
            min_val = apsl_val

        bgng_dt = str(r.get("입찰시작일시") or "")[:10]
        end_dt = str(r.get("입찰마감일시") or "")[:10]
        rate = (min_val / apsl_val) if apsl_val > 0 else -1.0
        dsps = str(r.get("처분방식") or "매각").strip()

        gongmae_rows.append({
            "구분_원본": "공매",
            "사건번호": cno,
            "종류": usg,
            "주소": addr,
            "기본": basic_str,
            "전용면적(평)": bldg_py,
            "대지권(평)": land_py,
            "특이사항": stat_str,
            "감정가(M)": apsl_val,
            "최저가(M)": min_val,
            "입찰일": bgng_dt,
            "입찰상황": end_dt,
            "최저가율": rate,
            "조회수": dsps,
        })

    # 경매 표준 행 변환
    kyungmae_rows = []
    for _, r in df_auction_refined.iterrows():
        cno = str(r.get("사건번호") or "").strip()
        if not cno or cno == "nan":
            continue
        raw_addr = str(r.get("주소") or "").strip()
        addr = (
            raw_addr.replace("경기도", "경기")
            .replace("서울특별시", "서울")
            .replace("인천광역시", "인천")
            .replace("충청남도", "충남")
            .replace("강원특별자치도", "강원")
            .replace("강원도", "강원")
            .replace("전라남도", "전남")
        )
        try:
            apsl_val = float(str(r.get("감정가") or "0").replace(",", ""))
        except Exception:
            apsl_val = 0.0
        try:
            min_val = float(str(r.get("최저가") or "0").replace(",", ""))
        except Exception:
            min_val = 0.0

        kyungmae_rows.append({
            "구분_원본": "경매",
            "사건번호": cno,
            "종류": str(r.get("종류") or "").strip(),
            "주소": addr,
            "기본": str(r.get("기본") or "").strip(),
            "전용면적(평)": float(r.get("전용면적(평)") or 0.0),
            "대지권(평)": float(r.get("대지권(평)") or 0.0),
            "특이사항": str(r.get("특이사항") or "0").strip(),
            "감정가(M)": apsl_val,
            "최저가(M)": min_val,
            "입찰일": str(r.get("입찰일") or "").strip(),
            "입찰상황": str(r.get("입찰상황") or "").strip(),
            "최저가율": float(r.get("낙찰율") or 0.0),
            "조회수": r.get("조회수"),
        })

    all_base_rows = gongmae_rows + kyungmae_rows
    log(f"  - 전체 결합 물건 수: {len(all_base_rows):,}건 (공매 {len(gongmae_rows):,}건 + 경매 {len(kyungmae_rows):,}건)")

    # 3단계: 신규 물건만 지오코딩 (기존 물건은 캐시 좌표 즉시 매칭)
    log("=" * 70)
    log("3단계: 신규 물건 KakaoGeocode 경도·위도 산출 (기존 물건 캐시 재사용)")
    log("=" * 70)

    new_addrs_to_geocode = set()
    matched_count = 0
    for item in all_base_rows:
        cno_key = item["사건번호"].replace(" ", "")
        addr_key = item["주소"].strip()
        if cno_key in by_case or addr_key in by_addr:
            matched_count += 1
        elif addr_key:
            new_addrs_to_geocode.add(addr_key)

    log(f"  - 기존 좌표 캐시 즉시 매칭: {matched_count:,}건")
    log(f"  - 신규 지오코딩 대상 고유 주소 수: {len(new_addrs_to_geocode):,}건")

    geocoded_new = {}
    if new_addrs_to_geocode:
        addr_list = list(new_addrs_to_geocode)
        done_cnt = 0
        with ThreadPoolExecutor(max_workers=10) as ex:
            future_map = {ex.submit(kakao_geocode_single, a): a for a in addr_list}
            for fut in as_completed(future_map):
                a = future_map[fut]
                done_cnt += 1
                try:
                    lng, lat = fut.result()
                    if lng > 120 and lat > 30:
                        geocoded_new[a] = compute_spatial_features_for_coord(lat, lng, ref)
                except Exception:
                    pass
                if done_cnt % 250 == 0 or done_cnt == len(addr_list):
                    log(f"    [KakaoGeocode 진행률] {done_cnt:,}/{len(addr_list):,} 완료 (성공: {len(geocoded_new):,}건)")

    # 4단계: 45개 전체 컬럼 완성
    log("=" * 70)
    log("4단계: 45개 표준 컬럼 계산 및 수의계약 분류 규칙 반영")
    log("=" * 70)

    type_map = ref.get("type_bf_bg") or {}
    hug_set = set(ref.get("hug_cases") or [])
    redev_list = ref.get("redev_au_list") or []
    aw_ax_list = ref.get("special_code_aw_ax") or []
    rp_map = ref.get("realprice_map") or {}
    school_regions = ref.get("school_regions") or []
    elite_groups = set(ref.get("elite_groups") or [])

    final_records = []
    suui_count = 0
    for item in all_base_rows:
        raw_div = item["구분_원본"]
        cno = item["사건번호"]
        cno_nospace = cno.replace(" ", "")
        kind = item["종류"]
        addr = item["주소"]
        basic = item["기본"]
        bldg_py = item["전용면적(평)"]
        land_py = item["대지권(평)"]
        spec_note = item["특이사항"]
        apsl_m = item["감정가(M)"]
        min_m = item["최저가(M)"]
        bid_dt = item["입찰일"]
        bid_stat = item["입찰상황"]
        min_rate = item["최저가율"]
        views = item["조회수"]

        # 형태(대분류) 매핑
        form_type = type_map.get(kind, "대분류없음")
        if form_type == "대분류없음":
            if any(k in kind for k in ["아파트", "주상복합"]):
                form_type = "아파트"
            elif any(k in kind for k in ["오피스텔"]):
                form_type = "오피스텔"
            elif any(k in kind for k in ["다세대", "연립", "빌라", "도시형"]):
                form_type = "다세대"
            elif any(k in kind for k in ["단독", "다가구"]):
                form_type = "단독"
            elif any(k in kind for k in ["근린", "상가", "점포", "판매", "업무", "사무"]):
                form_type = "집합"
            elif any(k in kind for k in ["지식산업", "아파트형공장"]):
                form_type = "지산"
            elif any(k in kind for k in ["대지", "전", "답", "임야", "잡종지", "과수원", "도로", "구거", "하천", "토지"]):
                form_type = "토지"

        # 주소 토큰 파싱 (시도, 시군구, 읍면동/리)
        parts = addr.split()
        sido_short = addr[:2] if len(addr) >= 2 else ""
        gu_name = parts[1] if len(parts) > 1 else ""
        dong_token = ""
        for p in parts[2:5]:
            if p.endswith(("동", "가", "읍", "면", "리")):
                dong_token = p
                break
        if not dong_token and len(parts) > 2:
            dong_token = parts[2]

        region_key = f"{sido_short}{dong_token}"

        # 실거래가 매핑
        rp_vals = rp_map.get(f"{region_key}|{form_type}", [0.0, 0.0])
        m2_price, py_price = rp_vals[0], rp_vals[1]

        # 평당최저가격 & 평당감정가격
        use_bldg_area = (bldg_py != 0) and (form_type in ("아파트", "다세대", "집합", "지산", "오피스텔"))
        denom_py = bldg_py if use_bldg_area else land_py
        min_per_py = (min_m / denom_py / 10000.0) if denom_py > 0 else 0.0
        apsl_per_py = (apsl_m / denom_py / 10000.0) if denom_py > 0 else 0.0
        gap_ratio = (min_per_py / apsl_per_py if apsl_per_py > 0 else 0.0) if py_price < 10 else (min_per_py / py_price if py_price > 0 else 0.0)

        # HUG포기 여부
        hug_flag = "HUG" if (cno_nospace in hug_set or "HUG" in spec_note.upper() or "주택도시보증공사" in spec_note) else "미해당"

        # 재개발 포함 여부
        redev_flag = "미포함"
        if dong_token:
            for r_item in redev_list:
                if r_item.startswith(dong_token):
                    redev_flag = "포함"
                    break

        # 특이사항1 & 특이코드
        if raw_div == "공매":
            spec_note_1 = f"공매, {spec_note}"
        else:
            spec_note_1 = spec_note if (spec_note and spec_note != "0") else "#"

        codes = []
        for kw, cd in aw_ax_list:
            if kw and kw in spec_note_1:
                codes.append(cd)
        spec_code = "".join(codes) if codes else ("B" if raw_div == "공매" else "A")

        # 수의계약 분류 규칙: '수의계약' 단어가 들어가기만 하면 구분='수의계약'
        combined_suui_check = f"{raw_div} {spec_note} {bid_stat} {spec_note_1} {views}"
        if "수의계약" in combined_suui_check:
            final_div = "수의계약"
            suui_count += 1
        else:
            final_div = raw_div

        # 학군 판정
        elite_flag = "No"
        if form_type in ("다세대", "단독", "아파트"):
            for sr in school_regions:
                if dong_token and dong_token in sr["dongs"] and sr["group"] in elite_groups:
                    elite_flag = "Yes"
                    break

        # 좌표 및 공간지표 결합
        sp = by_case.get(cno_nospace) or by_addr.get(addr) or geocoded_new.get(addr)
        if not sp:
            sp = compute_spatial_features_for_coord(0.0, 0.0, ref)

        final_records.append({
            "구분": final_div,
            "사건번호": cno,
            "종류": kind,
            "주소": addr,
            "기본": basic,
            "전용면적(평)": bldg_py,
            "대지권(평)": land_py,
            "특이사항": spec_note,
            "감정가(M)": apsl_m,
            "최저가(M)": min_m,
            "입찰일": bid_dt,
            "입찰상황": bid_stat,
            "최저가율": min_rate,
            "조회수": views,
            "지역": region_key,
            "m2당 가격": m2_price,
            "평당가격": py_price,
            "평당최저가격": min_per_py,
            "평당감정가격": apsl_per_py,
            "괴리율": gap_ratio,
            "사건번호.1": cno_nospace if raw_div == "공매" else cno,
            "HUG포기": hug_flag,
            "형태": form_type,
            "재개발": redev_flag,
            "해당구": gu_name,
            "특이사항1": spec_note_1,
            "특이코드": spec_code,
            "학군": elite_flag,
            "전철역": sp.get("전철역", "0"),
            "노선": sp.get("노선", "0"),
            "역거리": sp.get("역거리", 99999.0),
            "더블역세권": sp.get("더블역세권", 0),
            "GTX 거리": sp.get("GTX 거리", 99999.0),
            "GTX역사": sp.get("GTX역사", "0"),
            "중학교": sp.get("중학교", "0"),
            "반경": sp.get("반경", 99999.0),
            "산단": sp.get("산단", "0"),
            "산단거리": sp.get("산단거리", 99999.0),
            "대학명": sp.get("대학명", "0"),
            "대학거리": sp.get("대학거리", 99999.0),
            "세대수": sp.get("세대수", 0),
            "IC명": sp.get("IC명", "0"),
            "IC거리": sp.get("IC거리", 99999.0),
            "경도": sp.get("경도", 0.0),
            "위도": sp.get("위도", 0.0),
        })

    df_final_master = pd.DataFrame(final_records)
    log(f"  - 수의계약 자동 분류 건수: {suui_count:,}건")

    # 4-1. 두인경공매_rawdata의 [관심1] 및 [경매종합] 시트 업데이트 저장
    try:
        log(f"두인경공매_rawdata 워크북([관심1], [경매종합]) 업데이트 중: {RAWDATA_FIXED_PATH}")
        wb_raw = openpyxl.load_workbook(RAWDATA_FIXED_PATH)
        if "관심1" in wb_raw.sheetnames:
            ws_g1 = wb_raw["관심1"]
            # 기존 데이터 클리어 후 신규 온비드 데이터 + 경위도 기록
            if ws_g1.max_row > 1:
                ws_g1.delete_rows(2, ws_g1.max_row)
            ws_g1.cell(1, 25, "경도")
            ws_g1.cell(1, 26, "위도")
            ws_g1.cell(1, 34, KAKAO_REST_API_KEY)
            onbid_cols = list(df_onbid.columns)
            for r_idx, r_val in enumerate(df_onbid.values.tolist(), start=2):
                for c_idx, val in enumerate(r_val[:22], start=1):
                    ws_g1.cell(r_idx, c_idx, val)
                # 신규/기존 산출된 경도·위도 또는 KakaoGeocode 수식 세팅
                cno_v = str(r_val[1] if len(r_val) > 1 else "").replace(" ", "").strip()
                sp_v = by_case.get(cno_v)
                if not sp_v:
                    raw_nm = str(r_val[11] if len(r_val) > 11 else "").strip()
                    addr_norm = (
                        raw_nm.replace("경기도", "경기")
                        .replace("서울특별시", "서울")
                        .replace("인천광역시", "인천")
                        .replace("충청남도", "충남")
                        .replace("강원특별자치도", "강원")
                        .replace("전라남도", "전남")
                    )
                    sp_v = by_addr.get(addr_norm) or geocoded_new.get(addr_norm)
                if sp_v and float(sp_v.get("경도") or 0) > 120:
                    ws_g1.cell(r_idx, 25, float(sp_v["경도"]))
                    ws_g1.cell(r_idx, 26, float(sp_v["위도"]))
                else:
                    ws_g1.cell(r_idx, 25, f'=KakaoGeocode(L{r_idx},"{KAKAO_REST_API_KEY}",$Y$1)')
                    ws_g1.cell(r_idx, 26, f'=KakaoGeocode(L{r_idx},"{KAKAO_REST_API_KEY}",$Z$1)')

        if "경매종합" in wb_raw.sheetnames:
            ws_kj = wb_raw["경매종합"]
            if ws_kj.max_row > 1:
                ws_kj.delete_rows(2, ws_kj.max_row)
            for r_idx, r_val in enumerate(df_auction_refined.values.tolist(), start=2):
                for c_idx, val in enumerate(r_val, start=1):
                    ws_kj.cell(r_idx, c_idx, val)

        wb_raw.save(RAWDATA_FIXED_PATH)
        dated_raw = os.path.join(DOOIN_ROOT, f"두인경공매_rawdata{datetime.now().strftime('%y%m%d')}.xlsx")
        shutil.copy2(RAWDATA_FIXED_PATH, dated_raw)
        wb_raw.close()
        log(f"  ✅ 두인경공매_rawdata 저장 완료: {RAWDATA_FIXED_PATH} (백업: {os.path.basename(dated_raw)})")
    except Exception as e:
        log(f"  ⚠️ 두인경공매_rawdata 저장 중 경고 (마스터 파일 생성은 계속 진행): {e}")

    # 4-2. 두인경매_작업파일_1.xlsm의 맨 끝 시트([통합]) 업데이트
    try:
        log(f"두인경매_작업파일_1.xlsm [통합] 시트 업데이트 중: {WORKBOOK_1_PATH}")
        wb_w1 = openpyxl.load_workbook(WORKBOOK_1_PATH, keep_vba=True)
        target_sheet_name = "통합" if "통합" in wb_w1.sheetnames else wb_w1.sheetnames[-1]
        ws_t = wb_w1[target_sheet_name]
        if ws_t.max_row > 1:
            ws_t.delete_rows(2, ws_t.max_row)
        ws_t.cell(1, 37, "경도")
        ws_t.cell(1, 38, "위도")
        ws_t.cell(1, 39, KAKAO_REST_API_KEY)
        for r_idx, r_val in enumerate(df_auction_raw.values.tolist(), start=2):
            for c_idx, val in enumerate(r_val[:35], start=1):
                ws_t.cell(r_idx, c_idx, val)
            raw_ad = str(r_val[4] if len(r_val) > 4 else "").strip()
            addr_norm = (
                raw_ad.replace("경기도", "경기")
                .replace("서울특별시", "서울")
                .replace("인천광역시", "인천")
                .replace("충청남도", "충남")
                .replace("강원특별자치도", "강원")
                .replace("강원도", "강원")
                .replace("전라남도", "전남")
            )
            sp_v = by_addr.get(addr_norm) or geocoded_new.get(addr_norm)
            if sp_v and float(sp_v.get("경도") or 0) > 120:
                ws_t.cell(r_idx, 37, float(sp_v["경도"]))
                ws_t.cell(r_idx, 38, float(sp_v["위도"]))
            else:
                ws_t.cell(r_idx, 37, f'=KakaoGeocode(E{r_idx},"{KAKAO_REST_API_KEY}",$AK$1)')
                ws_t.cell(r_idx, 38, f'=KakaoGeocode(E{r_idx},"{KAKAO_REST_API_KEY}",$AL$1)')
        wb_w1.save(WORKBOOK_1_PATH)
        wb_w1.close()
        log(f"  ✅ 두인경매_작업파일_1.xlsm [{target_sheet_name}] 시트 저장 완료")
    except Exception as e:
        log(f"  ⚠️ 두인경매_작업파일_1.xlsm 업데이트 중 경고: {e}")

    # 4-3. 최종 경공매데이터_업데이트_대항력추가.xlsx 저장
    os.makedirs(UPDATE_DIR, exist_ok=True)
    backup_dir = os.path.join(UPDATE_DIR, "backups")
    os.makedirs(backup_dir, exist_ok=True)
    if os.path.exists(FINAL_EXCEL_PATH):
        bk_path = os.path.join(backup_dir, f"경공매데이터_업데이트_대항력추가_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
        shutil.copy2(FINAL_EXCEL_PATH, bk_path)
        log(f"  - 기존 마스터 엑셀 백업 완료: {bk_path}")

    df_final_master.to_excel(FINAL_EXCEL_PATH, index=False, engine="openpyxl")
    log(f"  ✅ 최종 마스터 엑셀 생성 완료: {FINAL_EXCEL_PATH} (총 {len(df_final_master):,}건)")
    return FINAL_EXCEL_PATH


def run_step5_db_and_aws_deploy(final_excel_path: str):
    """5단계: 로컬 SQLite DB(map_data.db) 반영 및 AWS EC2 원격 서버 자동 배포"""
    log("=" * 70)
    log("5단계: 로컬 DB 반영 및 AWS EC2 서버 자동 업로드 시작")
    log("=" * 70)

    import_script = os.path.join(VIBECODING_DIR, "backend", "scripts", "import_auction_data.py")
    flag_script = os.path.join(VIBECODING_DIR, "backend", "scripts", "flag_unexecuted_auctions.py")
    deploy_script = os.path.join(VIBECODING_DIR, "deploy_auction_update.py")

    log("▶ [로컬 DB] import_auction_data.py 실행 중...")
    subprocess.run([sys.executable, import_script, final_excel_path], cwd=VIBECODING_DIR, check=True)

    log("▶ [로컬 DB] flag_unexecuted_auctions.py 실행 중...")
    subprocess.run([sys.executable, flag_script], cwd=VIBECODING_DIR, check=True)

    # AWS SSH Key 경로 자동 보정
    ssh_key_cand1 = r"C:\Users\llll\.ssh\aws-key.pem"
    ssh_key_cand2 = r"C:\Users\llll\Downloads\aws-key.pem"
    env = os.environ.copy()
    if os.path.exists(ssh_key_cand1):
        env["AWS_KEY_PATH"] = ssh_key_cand1
    elif os.path.exists(ssh_key_cand2):
        env["AWS_KEY_PATH"] = ssh_key_cand2

    log("▶ [AWS EC2] deploy_auction_update.py 실행 중...")
    subprocess.run([sys.executable, deploy_script], cwd=VIBECODING_DIR, env=env, check=True)
    log("🎉 로컬 DB 및 AWS EC2 원격 배포가 모두 완료되었습니다!")


def main():
    parser = argparse.ArgumentParser(description="주간 경공매 자동 크롤링·지오코딩·통합·배포 파이프라인")
    parser.add_argument("--skip-crawl", action="store_true", help="크롤링 단계를 건너뛰고 가장 최근 수집된 엑셀 파일로 통합·지오코딩·배포 실행")
    parser.add_argument("--skip-deploy", action="store_true", help="로컬/AWS 배포 단계를 건너뛰고 엑셀 생성까지만 실행")
    args = parser.parse_args()

    start_ts = time.time()
    log("🚀 [주간 경·공매 자동화 파이프라인] 시작")

    if not args.skip_crawl:
        run_step1_crawlers()
    else:
        log("⏩ --skip-crawl 옵션에 따라 1단계 크롤링을 건너뛰고 최신 수집 파일을 사용합니다.")

    onbid_excel = get_latest_file(ONBID_DIR, "온비드_관심물건_*.xlsx")
    sudo_excel = get_latest_file(ONBID_DIR, "수도권_두인경매통합_*.xlsx")
    regional_excel = get_latest_file(ONBID_DIR, "지방권_두인경매통합_*.xlsx")

    if not onbid_excel or not sudo_excel or not regional_excel:
        raise FileNotFoundError(
            f"필수 크롤링 결과 파일을 찾을 수 없습니다: onbid={onbid_excel}, sudo={sudo_excel}, regional={regional_excel}"
        )

    final_excel = update_workbooks_and_build_master(onbid_excel, sudo_excel, regional_excel)

    if not args.skip_deploy:
        run_step5_db_and_aws_deploy(final_excel)
    else:
        log("⏩ --skip-deploy 옵션에 따라 DB/AWS 배포를 건너뛰었습니다.")

    elapsed = time.time() - start_ts
    log(f"✅ 전체 파이프라인 정상 종료 (총 소요시간: {elapsed/60:.1f}분)")


if __name__ == "__main__":
    main()
