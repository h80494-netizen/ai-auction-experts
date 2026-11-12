import os
import re
import sys
import glob
import math
import time
import sqlite3
import pandas as pd


def _extract_date_sort_key(filename: str) -> str:
    """파일명 내 YYYYMMDD 또는 YYMMDD 날짜를 추출하여 최신순 정렬 키로 반환"""
    m8 = re.search(r'(20\d{6})', filename)
    if m8:
        return m8.group(1)
    m6 = re.search(r'(?<!\d)(2\d{5})(?!\d)', filename)
    if m6:
        return "20" + m6.group(1)
    return "00000000"


def _classify_estate_type(raw_type: str, raw_detail: str, fallback_type: str) -> str:
    """파일명이 아닌 행 내부의 실제 '유형'/'상세유형' 컬럼 기준 정밀 분류"""
    t = f"{raw_type} {raw_detail}".strip()
    if not t or t == "nan nan":
        return fallback_type
    if any(k in t for k in ("아파트", "분양권", "재건축", "재개발")):
        if "오피스텔" in t:
            return "오피스텔"
        return "아파트"
    if any(k in t for k in ("오피스텔",)):
        return "오피스텔"
    if any(k in t for k in ("빌라", "연립", "다세대")):
        return "다세대/빌라"
    if any(k in t for k in ("단독", "다가구", "전원", "한옥", "상가주택")):
        return "단독주택"
    if any(k in t for k in ("토지", "임야", "전", "답", "대지", "과수원", "잡종지")):
        # 단, '전세' 오탐 방지를 위해 raw_type 자체 확인
        if any(k in raw_type for k in ("토지", "임야")) or any(k in raw_detail for k in ("토지", "임야")):
            return "토지"
    if any(k in t for k in ("상가", "사무실", "근린", "점포", "건물", "공장", "창고", "지식산업", "숙박")):
        return "상가"
    return fallback_type


def _clean_num_str(val, default_str: str = "") -> str:
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return default_str
    s = str(val).replace(",", "").strip()
    if not s or s.lower() in ("nan", "none", "-", "null"):
        return default_str
    try:
        f = float(s)
        if math.isnan(f):
            return default_str
        if f.is_integer():
            return str(int(f))
        return f"{f:.2f}".rstrip("0").rstrip(".")
    except Exception:
        return s


def _determine_fallback_meta(filename: str):
    if "인천" in filename:
        region = "인천"
    elif "서울" in filename:
        region = "서울"
    elif "경기" in filename:
        region = "경기"
    else:
        region = "전국"

    if "아파트" in filename:
        estate_type = "아파트"
    elif any(k in filename for k in ("빌라", "연립", "다세대")):
        estate_type = "다세대/빌라"
    elif "오피스텔" in filename:
        estate_type = "오피스텔"
    elif any(k in filename for k in ("단독", "다가구")):
        estate_type = "단독주택"
    elif "상가" in filename:
        estate_type = "상가"
    elif "토지" in filename:
        estate_type = "토지"
    else:
        estate_type = "기타"
    return region, estate_type


def _load_dataframe(file_path: str) -> pd.DataFrame:
    if file_path.lower().endswith(".csv"):
        for enc in ("utf-8-sig", "cp949", "euc-kr"):
            try:
                return pd.read_csv(file_path, encoding=enc, low_memory=False)
            except Exception:
                continue
        raise RuntimeError(f"CSV 인코딩 판독 실패: {file_path}")
    else:
        try:
            return pd.read_excel(file_path, engine="calamine")
        except Exception as e:
            print(f"  [WARN] Calamine 실패 ({os.path.basename(file_path)}): {e} -> openpyxl 재시도", flush=True)
            return pd.read_excel(file_path, engine="openpyxl")


def update_naver_db():
    start_time = time.time()
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(backend_dir)
    data_dir = os.path.join(base_dir, "data", "네이버부동산")
    crawl_autosave_dir = os.path.join(os.path.dirname(base_dir), "네이버부동산크롤링", "자동저장")
    db_path = os.path.join(backend_dir, "data", "map_data.db")

    if not os.path.exists(data_dir) and not os.path.exists(crawl_autosave_dir):
        print(f"Data directory not found: {data_dir}")
        return

    print(f"Connecting to database: {db_path}", flush=True)
    conn = sqlite3.connect(db_path, timeout=60.0)
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    cursor = conn.cursor()

    drop_table = "--drop" in sys.argv
    if drop_table:
        print("Dropping existing naver_real_estate table...", flush=True)
        cursor.execute("DROP TABLE IF EXISTS naver_real_estate")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS naver_real_estate (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            estate_id TEXT UNIQUE,
            address TEXT,
            price TEXT,
            rent TEXT,
            floor TEXT,
            area TEXT,
            deal_type TEXT,
            type_detail TEXT,
            lat REAL,
            lng REAL,
            estate_type TEXT,
            region TEXT,
            age_info TEXT
        )
    """)
    conn.commit()

    filter_keywords = [arg for arg in sys.argv[1:] if not arg.startswith("--")]

    # 1. 크롤링 자동저장 CSV 원본 스캔 (최신 수집분 우선 반영)
    sources = []
    has_autosave_csvs = False
    if os.path.exists(crawl_autosave_dir):
        autosave_csvs = sorted(
            glob.glob(os.path.join(crawl_autosave_dir, "크롤링_자동저장_*.csv")),
            key=lambda p: _extract_date_sort_key(os.path.basename(p)),
            reverse=True
        )
        for fp in autosave_csvs:
            fn = os.path.basename(fp)
            if filter_keywords and not any(kw in fn for kw in filter_keywords):
                continue
            sources.append({
                "path": fp,
                "file": f"[크롤러자동저장] {fn}",
                "fallback_region": "전국",
                "fallback_type": "기타",
                "sort_key": ("1_autosave", _extract_date_sort_key(fn)),
            })
        if autosave_csvs and not filter_keywords:
            has_autosave_csvs = True

    # 2. 워크스페이스 data/네이버부동산 폴더 내 매매/개별 데이터셋 스캔
    if os.path.exists(data_dir):
        local_files = []
        for fn in os.listdir(data_dir):
            if not fn.lower().endswith((".xlsx", ".xlsm", ".csv")) or fn.startswith("~$"):
                continue
            # 자동저장 CSV 원본이 존재할 경우, 중복·오분류 원인인 누적 Part 스냅샷(전월세/상가월세 Part*) 제외
            if has_autosave_csvs and re.search(r"(전월세|상가월세).*_Part\d+", fn):
                print(f"  [SKIP] 누적 중복 스냅샷 제외 (자동저장 CSV 원본으로 대체): {fn}", flush=True)
                continue
            if filter_keywords and not any(kw in fn for kw in filter_keywords):
                continue
            f_region, f_type = _determine_fallback_meta(fn)
            local_files.append({
                "path": os.path.join(data_dir, fn),
                "file": fn,
                "fallback_region": f_region,
                "fallback_type": f_type,
                "sort_key": ("0_standalone", _extract_date_sort_key(fn)),
            })
        local_files.sort(key=lambda x: x["sort_key"][1], reverse=True)
        sources.extend(local_files)

    print(f"\n총 {len(sources)}개 데이터 소스를 최신일자 우선순위로 적재합니다:", flush=True)
    for s in sources:
        print(f"  - {s['file']} (기본지역: {s['fallback_region']}, 기본유형: {s['fallback_type']})", flush=True)
    print("-" * 70, flush=True)

    insert_sql = """
        INSERT OR IGNORE INTO naver_real_estate
        (estate_id, address, price, rent, floor, area, deal_type, type_detail, lat, lng, estate_type, region, age_info)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    seen_ids = set()
    if not drop_table:
        cursor.execute("SELECT estate_id FROM naver_real_estate")
        seen_ids = {r[0] for r in cursor.fetchall() if r[0]}

    total_new_records = 0

    for item in sources:
        file_path = item["path"]
        label = item["file"]
        fallback_region = item["fallback_region"]
        fallback_type = item["fallback_type"]

        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            print(f"Skipping missing/empty file: {label}", flush=True)
            continue

        t_load = time.time()
        try:
            df = _load_dataframe(file_path)
        except Exception as e:
            print(f"  [ERROR] Failed to read {label}: {e}", flush=True)
            continue

        n_rows = len(df)
        if n_rows == 0:
            continue

        cols = set(df.columns)
        col_id = df["매물 번호"].tolist() if "매물 번호" in cols else [""] * n_rows
        col_addr = df["매물위치(주소)"].tolist() if "매물위치(주소)" in cols else [""] * n_rows
        col_price = (
            df["매매가(보증금)"].tolist()
            if "매매가(보증금)" in cols
            else (df["금액"].tolist() if "금액" in cols else [""] * n_rows)
        )
        col_rent = df["월세"].tolist() if "월세" in cols else ["0"] * n_rows
        col_floor = df["층수"].tolist() if "층수" in cols else [""] * n_rows
        col_tfloor = df["전체층"].tolist() if "전체층" in cols else [""] * n_rows
        # 전용면적(㎡) 최우선 저장 -> 공급면적(㎡) 차선 (app.py 및 naver_price_analyzer.py 모두 ㎡÷3.3058 사용)
        col_jeonyong = df["전용면적"].tolist() if "전용면적" in cols else [None] * n_rows
        col_gonggeup = df["공급면적"].tolist() if "공급면적" in cols else [None] * n_rows
        col_deal = df["거래유형"].tolist() if "거래유형" in cols else ["매매"] * n_rows
        col_utype = df["유형"].tolist() if "유형" in cols else [""] * n_rows
        col_udetail = df["상세유형"].tolist() if "상세유형" in cols else [""] * n_rows
        col_lat = pd.to_numeric(df["위도"], errors="coerce").tolist() if "위도" in cols else [0.0] * n_rows
        col_lng = pd.to_numeric(df["경도"], errors="coerce").tolist() if "경도" in cols else [0.0] * n_rows
        col_desc = df["보조설명"].tolist() if "보조설명" in cols else [""] * n_rows
        col_rcode = df["지역코드"].tolist() if "지역코드" in cols else [""] * n_rows

        records = []
        for idx in range(n_rows):
            lat = col_lat[idx]
            lng = col_lng[idx]
            if lat is None or lng is None or math.isnan(lat) or math.isnan(lng) or lat <= 0.0 or lng <= 0.0:
                continue

            eid = _clean_num_str(col_id[idx], "")
            if not eid or eid in seen_ids:
                continue
            seen_ids.add(eid)

            raw_addr = col_addr[idx]
            address = "" if pd.isna(raw_addr) else str(raw_addr).strip()
            if address.lower() == "nan":
                address = ""

            price = _clean_num_str(col_price[idx], "0")
            rent = _clean_num_str(col_rent[idx], "0")

            fl_raw = "" if pd.isna(col_floor[idx]) else str(col_floor[idx]).strip()
            if fl_raw.lower() in ("nan", "none"):
                fl_raw = ""
            tfl_raw = _clean_num_str(col_tfloor[idx], "")
            if fl_raw and "/" not in fl_raw and tfl_raw and tfl_raw != "-":
                fl_clean = fl_raw.replace("층", "").strip()
                floor = f"{fl_clean}/{tfl_raw}층"
            else:
                floor = fl_raw

            area = _clean_num_str(col_jeonyong[idx], "")
            if not area or area == "0":
                area = _clean_num_str(col_gonggeup[idx], "0")

            deal_raw = col_deal[idx]
            deal_type = "매매" if pd.isna(deal_raw) else str(deal_raw).strip()
            if not deal_type or deal_type.lower() == "nan":
                deal_type = "매매"

            u_str = "" if pd.isna(col_utype[idx]) else str(col_utype[idx]).strip()
            ud_str = "" if pd.isna(col_udetail[idx]) else str(col_udetail[idx]).strip()
            estate_type = _classify_estate_type(u_str, ud_str, fallback_type)
            type_detail = ud_str if ud_str and ud_str.lower() != "nan" else estate_type

            desc_raw = "" if pd.isna(col_desc[idx]) else str(col_desc[idx])
            age_info = ""
            if "년" in desc_raw:
                parts = [p.strip() for p in desc_raw.split(",") if "년" in p]
                if parts:
                    age_info = parts[0]

            rcode = _clean_num_str(col_rcode[idx], "")
            if rcode.startswith("11"):
                row_region = "서울"
            elif rcode.startswith("28"):
                row_region = "인천"
            elif rcode.startswith("41"):
                row_region = "경기"
            elif fallback_region != "전국":
                row_region = fallback_region
            elif "서울" in address:
                row_region = "서울"
            elif "인천" in address:
                row_region = "인천"
            elif "경기" in address:
                row_region = "경기"
            else:
                row_region = "전국"

            records.append((
                eid, address, price, rent, floor, area,
                deal_type, type_detail, float(lat), float(lng),
                estate_type, row_region, age_info
            ))

        if records:
            cursor.executemany(insert_sql, records)
            conn.commit()
            total_new_records += len(records)

        print(
            f"  ✓ {label}: 원본 {n_rows:,}행 -> 신규 적재 {len(records):,}건 ({time.time() - t_load:.2f}s)",
            flush=True
        )

    molit_added = append_molit_jeonwolse_records(conn, cursor)
    total_new_records += molit_added

    print("\nCreating indexes...", flush=True)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_naver_estate_id ON naver_real_estate(estate_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_naver_type_coords ON naver_real_estate(estate_type, lat, lng)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_naver_region_type_coords ON naver_real_estate(region, estate_type, lat, lng)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_naver_coords ON naver_real_estate(lat, lng)")
    conn.commit()

    print("\n=== Data Statistics in DB (지역 × 매물유형 × 거래유형) ===", flush=True)
    cursor.execute("""
        SELECT region, estate_type, deal_type, count(*)
        FROM naver_real_estate
        GROUP BY region, estate_type, deal_type
        ORDER BY region, estate_type, deal_type
    """)
    for reg, etype, dtype, cnt in cursor.fetchall():
        print(f"  {reg:4s} | {etype:8s} | {dtype:6s} | {cnt:>9,}건", flush=True)

    cursor.execute("SELECT count(*) FROM naver_real_estate")
    total_count = cursor.fetchone()[0]
    print(f"\nTotal Unique Records in DB: {total_count:,}건 (이번 신규 적재: {total_new_records:,}건)", flush=True)
    conn.close()

    rebuild_naver_pickle_caches()
    print(f"\nDatabase & cache update complete in {time.time() - start_time:.2f}s!", flush=True)

def append_molit_jeonwolse_records(conn, cursor):
    """
    국토부 전월세 실거래 CSV(data/실거래가/MOLIT_*_전월세_*.csv)를 오프라인 정밀 지오코더로 좌표 매핑하여
    naver_real_estate 테이블에 전월세(전세/월세) 보완 표본(estate_id='MOLIT_...')으로 적재합니다.
    - 매매 평당가 및 매물 리스트에는 영향을 주지 않으며(deal_type='전세'/'월세'),
      다세대/빌라, 오피스텔, 단독주택, 아파트 등의 환산보증금(보증금 + 월세×100) 및 전세가율 산출에 활용됩니다.
    """
    t0 = time.time()
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

    try:
        import load_realprice_data as lrd
    except Exception as e:
        print(f"  [WARN] load_realprice_data 모듈 로드 실패: {e}", flush=True)
        return 0

    print("\n=== Appending MOLIT 전월세 Records for Jeonse Ratio Calculation ===", flush=True)
    cursor.execute("DELETE FROM naver_real_estate WHERE estate_id LIKE 'MOLIT_%'")
    conn.commit()

    geocoder_pack = lrd.build_offline_geocoder(conn)
    selected, _ = lrd.select_latest_molit_files()
    global_memo = {}

    sido_map = {
        "서울특별시": ("서울", "SL"),
        "경기도": ("경기", "GG"),
        "인천광역시": ("인천", "IC"),
        "충청남도": ("전국", "CN"),
        "강원특별자치도": ("전국", "GW"),
    }
    ptype_map = {
        "연립다세대": ("다세대/빌라", "VL", 5),
        "오피스텔": ("오피스텔", "OP", 15),
        "단독다가구": ("단독주택", "DD", 3),
        "아파트": ("아파트", "AP", 15),
    }

    insert_sql = """
        INSERT OR IGNORE INTO naver_real_estate
        (estate_id, address, price, rent, floor, area, deal_type, type_detail, lat, lng, estate_type, region, age_info)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    total_added = 0
    for (sido, ptype, dtype), (seq, fp, sz, is_fb) in sorted(selected.items()):
        if dtype != "전월세" or sido not in sido_map or ptype not in ptype_map:
            continue
        t_file = time.time()
        region_label, sido_code = sido_map[sido]
        estate_type_label, ptype_code, default_tfl = ptype_map[ptype]

        try:
            df = pd.read_csv(fp, skiprows=15, encoding="cp949", low_memory=False)
        except Exception:
            try:
                df = pd.read_csv(fp, skiprows=15, encoding="utf-8-sig", low_memory=False)
            except Exception as e:
                print(f"  [WARN] 읽기 실패 ({os.path.basename(fp)}): {e}", flush=True)
                continue

        df.columns = [c.strip() for c in df.columns]
        if "시군구" not in df.columns or len(df) == 0:
            continue

        if "해제사유발생일" in df.columns:
            c_col = df["해제사유발생일"].fillna("-").astype(str).str.strip()
            df = df[c_col.isin(["-", "", "nan", "None"])]
            if len(df) == 0:
                continue

        area_col = next(
            (c for c in ("전용면적(㎡)", "계약면적(㎡)", "연면적(㎡)", "건물면적(㎡)") if c in df.columns),
            None,
        )
        dcol = "보증금(만원)" if "보증금(만원)" in df.columns else ("보증금" if "보증금" in df.columns else None)
        rcol = next((rc for rc in ("월세금(만원)", "월세(만원)", "월세금", "월세") if rc in df.columns), None)
        if not area_col or not dcol:
            continue

        df["_area_m2"] = lrd.clean_num_series(df[area_col]).fillna(0.0)
        df["_dep_man"] = lrd.clean_num_series(df[dcol]).fillna(0.0)
        df["_rent_man"] = lrd.clean_num_series(df[rcol]).fillna(0.0) if rcol else 0.0
        df = df[(df["_area_m2"] > 3.0) & ((df["_dep_man"] > 0) | (df["_rent_man"] > 0))].copy()
        if len(df) == 0:
            continue

        df["_area_rnd"] = df["_area_m2"].round(0).astype(int)
        df["_fl_num"] = pd.to_numeric(df["층"], errors="coerce").fillna(0).astype(int) if "층" in df.columns else 0
        df["_by_num"] = pd.to_numeric(df["건축년도"], errors="coerce").fillna(0).astype(int) if "건축년도" in df.columns else 0
        df["_ym_num"] = pd.to_numeric(df["계약년월"], errors="coerce").fillna(0).astype(int) if "계약년월" in df.columns else 0

        bcol = "단지명" if "단지명" in df.columns else ("건물명" if "건물명" in df.columns else None)
        # 최신 계약 우선 정렬 후 동일 건물·층·평형·전월세구분 중복 제거
        df = df.sort_values(by="_ym_num", ascending=False)
        dedup_cols = ["시군구"]
        if "번지" in df.columns and ptype != "단독다가구":
            dedup_cols.append("번지")
        elif "도로명" in df.columns:
            dedup_cols.append("도로명")
        if bcol:
            dedup_cols.append(bcol)
        dedup_cols.extend(["_fl_num", "_area_rnd"])
        if "전월세구분" in df.columns:
            dedup_cols.append("전월세구분")
        df = df.drop_duplicates(subset=dedup_cols, keep="first").reset_index(drop=True)

        lats, lngs, _ = lrd.resolve_coords_memoized(df, geocoder_pack, global_memo)
        valid_idx = [i for i in range(len(df)) if not (math.isnan(lats[i]) or math.isnan(lngs[i]) or lats[i] <= 0 or lngs[i] <= 0)]
        if not valid_idx:
            continue

        sgg_list = df["시군구"].fillna("").astype(str).str.strip().tolist()
        jibun_list = df["번지"].fillna("").astype(str).str.strip().tolist() if "번지" in df.columns else [""] * len(df)
        bldg_list = df[bcol].fillna("").astype(str).str.strip().tolist() if bcol else [""] * len(df)
        dep_list = df["_dep_man"].tolist()
        rent_list = df["_rent_man"].tolist()
        area_list = df["_area_m2"].tolist()
        fl_list = df["_fl_num"].tolist()
        by_list = df["_by_num"].tolist()

        batch_records = []
        for i in valid_idx:
            eid = f"MOLIT_{sido_code}_{ptype_code}_{i}"
            sgg_s = sgg_list[i]
            jb_s = jibun_list[i] if jibun_list[i] and "*" not in jibun_list[i] and jibun_list[i] != "nan" else ""
            bd_s = bldg_list[i] if bldg_list[i] and bldg_list[i] != "nan" else ""
            addr_str = " ".join(p for p in (sgg_s, jb_s, bd_s) if p).strip()

            dep_m = dep_list[i]
            rent_m = max(0.0, rent_list[i])
            # 보증금이 100억(1,000,000만원) 초과인 경우 원 단위로 변환하여 저장, 그 이하는 만원 단위 그대로 저장
            price_str = str(int(round(dep_m * 10000))) if dep_m > 1000000 else str(int(round(dep_m)))
            rent_str = str(int(round(rent_m))) if rent_m == int(rent_m) else f"{rent_m:.1f}"

            fl_val = fl_list[i]
            if fl_val < 0:
                floor_str = f"B{abs(fl_val)}/{default_tfl}층"
            elif fl_val > 0:
                tfl = max(default_tfl, fl_val)
                floor_str = f"{fl_val}/{tfl}층"
            else:
                floor_str = f"2/{default_tfl}층"

            area_str = f"{area_list[i]:.2f}"
            deal_str = "월세" if rent_m > 0 else "전세"
            by_val = by_list[i]
            age_str = f"{by_val}년" if by_val > 1900 else "25년이내"

            batch_records.append((
                eid,
                addr_str,
                price_str,
                rent_str,
                floor_str,
                area_str,
                deal_str,
                estate_type_label,
                float(lats[i]),
                float(lngs[i]),
                estate_type_label,
                region_label,
                age_str,
            ))

        if batch_records:
            cursor.executemany(insert_sql, batch_records)
            conn.commit()
            total_added += len(batch_records)
            print(
                f"  ✓ [MOLIT 전월세] {sido} {ptype} ({estate_type_label}): {len(batch_records):,}건 적재 ({time.time() - t_file:.1f}s)",
                flush=True,
            )

    print(f"=== Total MOLIT 전월세 Records Appended: {total_added:,}건 ({time.time() - t0:.1f}s) ===", flush=True)
    return total_added


def rebuild_naver_pickle_caches():
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(backend_dir)
    data_dir = os.path.join(project_root, "data", "네이버부동산")
    if os.path.exists(data_dir):
        for pkl_f in glob.glob(os.path.join(data_dir, ".cache_naver_*.pkl")):
            try:
                os.remove(pkl_f)
                print(f"Removed stale cache: {os.path.basename(pkl_f)}", flush=True)
            except Exception:
                pass

    print("\nRebuilding .cache_naver_*.pkl caches from updated DB...", flush=True)
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    import naver_price_analyzer
    naver_price_analyzer._DATASET_CACHE.clear()
    for target_t in ("아파트", "다세대/빌라", "오피스텔", "단독주택", "상가"):
        t0 = time.time()
        cdf = naver_price_analyzer.get_cached_dataset(target_t)
        cnt = len(cdf) if cdf is not None else 0
        deals = cdf["deal_type_val"].value_counts().to_dict() if cdf is not None and not cdf.empty else {}
        print(f"  ✓ Cache [{target_t}]: {cnt:,}건 ({deals}) in {time.time() - t0:.2f}s", flush=True)


def run_jeonwolse_only():
    start_time = time.time()
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(backend_dir, "data", "map_data.db")
    conn = sqlite3.connect(db_path, timeout=60.0)
    cursor = conn.cursor()
    added = append_molit_jeonwolse_records(conn, cursor)
    print("\n=== Data Statistics in DB (지역 × 매물유형 × 거래유형) ===", flush=True)
    cursor.execute("""
        SELECT region, estate_type, deal_type, count(*)
        FROM naver_real_estate
        GROUP BY region, estate_type, deal_type
        ORDER BY region, estate_type, deal_type
    """)
    for reg, etype, dtype, cnt in cursor.fetchall():
        print(f"  {reg:4s} | {etype:8s} | {dtype:6s} | {cnt:>9,}건", flush=True)
    conn.close()
    rebuild_naver_pickle_caches()
    print(f"\nJeonwolse sync & cache rebuild complete (+{added:,}건) in {time.time() - start_time:.2f}s!", flush=True)


if __name__ == "__main__":
    if "--jeonwolse-only" in sys.argv:
        run_jeonwolse_only()
    else:
        update_naver_db()
