import os
import glob
import json
import time
import datetime
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import openpyxl
import pandas as pd
import requests

from config import BASE_DIR, ONBID_CONFIG


SNAPSHOT_INDEX_PATH = os.path.join(BASE_DIR, "onbid_snapshot_index.json")
ARCHIVED_STATUS_KEYWORDS = ("공매취소", "수의계약회수", "유찰후회수", "개찰전취소")

# 게이트웨이 초당 호출 제한(TPS) 초과 방지를 위한 전역 레이트 리미터
_RATE_LOCK = threading.Lock()
_LAST_CALL_TS = 0.0
_MIN_CALL_INTERVAL = 0.25  # 초당 최대 4회로 안전하게 간격 유지


def format_date(val):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    s = str(val).strip()
    if s.endswith(".0"):
        s = s[:-2]
    if len(s) >= 12 and s[:12].isdigit():
        return f"{s[0:4]}-{s[4:6]}-{s[6:8]} {s[8:10]}:{s[10:12]}"
    if len(s) == 8 and s.isdigit():
        return f"{s[0:4]}-{s[4:6]}-{s[6:8]}"
    return s


def extract_date_from_filename(filepath):
    basename = os.path.basename(filepath)
    parts = basename.replace(".xlsx", "").split("_")
    for p in parts:
        if len(p) == 8 and p.isdigit():
            return f"{p[0:4]}-{p[4:6]}-{p[6:8]}"
    mtime = os.path.getmtime(filepath)
    return datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")


def load_json_file(filepath, default_val):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[경고] 캐시 파일 로드 실패 ({filepath}): {e}", flush=True)
    return default_val


def save_json_file(filepath, data):
    tmp_path = filepath + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, filepath)


def _parse_single_snapshot_excel(fpath):
    """단일 과거 엑셀 파일에서 활성 물건 스냅샷 행들을 추출합니다."""
    fname = os.path.basename(fpath)
    seen_date = extract_date_from_filename(fpath)
    parsed_rows = []

    wb = openpyxl.load_workbook(fpath, read_only=True, data_only=True)
    ws = wb.active
    rows_iter = ws.iter_rows(values_only=True)
    headers = next(rows_iter, None)
    if not headers:
        wb.close()
        return fname, seen_date, parsed_rows

    col_idx = {str(h).strip(): i for i, h in enumerate(headers) if h is not None}

    def get_val(row, *candidates):
        for c in candidates:
            idx = col_idx.get(c)
            if idx is not None and idx < len(row) and row[idx] is not None:
                val = str(row[idx]).strip()
                if val != "" and val.lower() != "nan":
                    return row[idx]
        return ""

    for row in rows_iter:
        cltr_mng_no = str(get_val(row, "물건관리번호")).strip()
        if not cltr_mng_no:
            continue

        status_text = str(get_val(row, "물건상태", "계약상태", "입찰결과")).strip()
        # 이미 과거 취소/회수로 병합되어 기록된 행은 활성 목격 이력에서 제외
        if any(k in status_text for k in ARCHIVED_STATUS_KEYWORDS):
            continue

        addr = str(get_val(row, "소재지", "상세주소")).strip()
        if not addr:
            sd = str(get_val(row, "시도")).strip()
            sgg = str(get_val(row, "시군구")).strip()
            emd = str(get_val(row, "읍면동")).strip()
            addr = " ".join(x for x in [sd, sgg, emd] if x)

        parsed_rows.append(
            {
                "cltrMngNo": cltr_mng_no,
                "pbctNo": str(get_val(row, "공매번호")).strip(),
                "last_seen_date": seen_date,
                "last_seen_file": fname,
                "last_status": status_text,
                "is_pvct": ("수의" in status_text),
                "prptDivNm": str(get_val(row, "재산유형", "재산유형명")).strip(),
                "pbctNsq": str(get_val(row, "회차")).strip(),
                "pbctsn": str(get_val(row, "차수")).strip(),
                "orgNm": str(get_val(row, "공고기관")).strip(),
                "usgNm": str(get_val(row, "용도", "용도(소분류)", "용도(중분류)")).strip(),
                "onbidCltrNm": str(get_val(row, "물건명")).strip(),
                "addr": addr,
                "landSqms": get_val(row, "토지면적(㎡)"),
                "bldSqms": get_val(row, "건물면적(㎡)"),
                "dspsMthodNm": str(get_val(row, "처분방식")).strip(),
                "apslEvlAmt": get_val(row, "감정가(원)", "감정평가금액"),
                "lowstBidPrc": get_val(row, "최저입찰가(원)", "최저입찰가격"),
                "bidRto": get_val(row, "최저입찰가율(%)"),
                "bidBgngDt": str(get_val(row, "입찰시작일시")).strip(),
                "bidEndDt": str(get_val(row, "입찰마감일시", "입찰종료일시")).strip(),
            }
        )

    wb.close()
    return fname, seen_date, parsed_rows


def build_historical_snapshot_index():
    """
    기존에 저장된 온비드_관심물건_*.xlsx 파일들을 병렬로 읽어
    물건관리번호별 마지막 목격 정보 인덱스를 생성/갱신합니다.
    """
    index_data = load_json_file(SNAPSHOT_INDEX_PATH, {"processed_files": [], "items": {}})
    processed_set = set(index_data.get("processed_files", []))
    items_map = index_data.get("items", {})

    excel_files = sorted(
        [
            f
            for f in glob.glob(os.path.join(BASE_DIR, "온비드_관심물건_*.xlsx"))
            if "요약" not in os.path.basename(f)
        ],
        key=lambda p: os.path.basename(p),
    )

    new_files = [f for f in excel_files if os.path.basename(f) not in processed_set]
    if not new_files:
        return items_map

    print(f"[과거 이력 스캔] 미인덱싱 엑셀 파일 {len(new_files)}개 병렬 분석 중...", flush=True)
    results = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(_parse_single_snapshot_excel, f): f for f in new_files}
        for fut in as_completed(futures):
            fpath = futures[fut]
            try:
                fname, seen_date, rows = fut.result()
                results.append((fname, seen_date, rows))
                print(f"  - {fname} 로드 완료 ({len(rows):,}건)", flush=True)
            except Exception as e:
                print(f"  - [경고] {os.path.basename(fpath)} 로드 실패 (인덱싱 제외 처리): {e}", flush=True)
                processed_set.add(os.path.basename(fpath))

    # 날짜/파일명 오름차순으로 병합하여 최신 스냅샷 값이 최종 반영되도록 정렬
    results.sort(key=lambda x: (x[1], x[0]))
    for fname, _, rows in results:
        for r in rows:
            cid = r["cltrMngNo"]
            prev = items_map.get(cid, {})
            ever_pvct = prev.get("ever_pvct", False) or r["is_pvct"]
            items_map[cid] = {
                "cltrMngNo": cid,
                "pbctNo": r["pbctNo"] or prev.get("pbctNo", ""),
                "last_seen_date": r["last_seen_date"],
                "last_seen_file": fname,
                "last_status": r["last_status"] or prev.get("last_status", ""),
                "ever_pvct": ever_pvct,
                "prptDivNm": r["prptDivNm"] or prev.get("prptDivNm", ""),
                "pbctNsq": r["pbctNsq"] or prev.get("pbctNsq", ""),
                "pbctsn": r["pbctsn"] or prev.get("pbctsn", ""),
                "orgNm": r["orgNm"] or prev.get("orgNm", ""),
                "usgNm": r["usgNm"] or prev.get("usgNm", ""),
                "onbidCltrNm": r["onbidCltrNm"] or prev.get("onbidCltrNm", ""),
                "addr": r["addr"] or prev.get("addr", ""),
                "landSqms": r["landSqms"] if r["landSqms"] != "" else prev.get("landSqms", ""),
                "bldSqms": r["bldSqms"] if r["bldSqms"] != "" else prev.get("bldSqms", ""),
                "dspsMthodNm": r["dspsMthodNm"] or prev.get("dspsMthodNm", ""),
                "apslEvlAmt": r["apslEvlAmt"] if r["apslEvlAmt"] != "" else prev.get("apslEvlAmt", 0),
                "lowstBidPrc": r["lowstBidPrc"] if r["lowstBidPrc"] != "" else prev.get("lowstBidPrc", 0),
                "bidRto": r["bidRto"] if r["bidRto"] != "" else prev.get("bidRto", ""),
                "bidBgngDt": r["bidBgngDt"] or prev.get("bidBgngDt", ""),
                "bidEndDt": r["bidEndDt"] or prev.get("bidEndDt", ""),
            }
        processed_set.add(fname)

    index_data["processed_files"] = sorted(processed_set)
    index_data["items"] = items_map
    save_json_file(SNAPSHOT_INDEX_PATH, index_data)
    return items_map


def update_snapshot_index_from_live_df(items_map, df_live):
    """오늘 수집된 실시간 활성 물건들을 스냅샷 인덱스에 반영합니다."""
    if df_live is None or df_live.empty:
        return
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    for _, row in df_live.iterrows():
        cid = str(row.get("cltrMngNo", "")).strip()
        if not cid:
            continue
        prev = items_map.get(cid, {})
        stat_nm = str(row.get("pbctStatNm") or "").strip()
        if not stat_nm:
            stat_nm = str(row.get("pvctTrgtYn_text") or "").strip()
        ever_pvct = prev.get("ever_pvct", False) or ("수의" in stat_nm)
        usg = (
            row.get("cltrUsgSclsCtgrNm")
            if pd.notna(row.get("cltrUsgSclsCtgrNm")) and row.get("cltrUsgSclsCtgrNm")
            else row.get("cltrUsgMclsCtgrNm", "")
        )
        items_map[cid] = {
            "cltrMngNo": cid,
            "pbctNo": str(row.get("pbctNo") or prev.get("pbctNo", "")).strip(),
            "last_seen_date": today_str,
            "last_seen_file": "LIVE_API",
            "last_status": stat_nm,
            "ever_pvct": ever_pvct,
            "prptDivNm": str(row.get("prptDivNm") or prev.get("prptDivNm", "")).strip(),
            "pbctNsq": str(row.get("pbctNsq") or prev.get("pbctNsq", "")).strip(),
            "pbctsn": str(row.get("pbctsn") or prev.get("pbctsn", "")).strip(),
            "orgNm": str(row.get("orgNm") or prev.get("orgNm", "")).strip(),
            "usgNm": str(usg or prev.get("usgNm", "")).strip(),
            "onbidCltrNm": str(row.get("onbidCltrNm") or prev.get("onbidCltrNm", "")).strip(),
            "addr": str(row.get("cltrRadr") or prev.get("addr", "")).strip(),
            "landSqms": row.get("landSqms") if pd.notna(row.get("landSqms")) else prev.get("landSqms", ""),
            "bldSqms": row.get("bldSqms") if pd.notna(row.get("bldSqms")) else prev.get("bldSqms", ""),
            "dspsMthodNm": str(row.get("dspsMthodNm") or prev.get("dspsMthodNm", "")).strip(),
            "apslEvlAmt": row.get("apslEvlAmt") if pd.notna(row.get("apslEvlAmt")) else prev.get("apslEvlAmt", 0),
            "lowstBidPrc": row.get("lowstBidPrcIndctCont") if pd.notna(row.get("lowstBidPrcIndctCont")) else prev.get("lowstBidPrc", 0),
            "bidRto": row.get("apslPrcCtrsLowstBidRto") if pd.notna(row.get("apslPrcCtrsLowstBidRto")) else prev.get("bidRto", ""),
            "bidBgngDt": format_date(row.get("cltrBidBgngDt")) or prev.get("bidBgngDt", ""),
            "bidEndDt": format_date(row.get("cltrBidEndDt")) or prev.get("bidEndDt", ""),
        }

    index_data = load_json_file(SNAPSHOT_INDEX_PATH, {"processed_files": [], "items": {}})
    index_data["items"] = items_map
    save_json_file(SNAPSHOT_INDEX_PATH, index_data)


def safe_int(v):
    try:
        return int(str(v).strip())
    except Exception:
        return 0


def _throttle_request():
    global _LAST_CALL_TS
    with _RATE_LOCK:
        now = time.monotonic()
        wait = _MIN_CALL_INTERVAL - (now - _LAST_CALL_TS)
        if wait > 0:
            time.sleep(wait)
        _LAST_CALL_TS = time.monotonic()


def query_single_bid_rslt_dtl(cltr_mng_no, stop_event=None):
    if stop_event is not None and stop_event.is_set():
        return "SKIPPED", {}

    params = {
        "serviceKey": ONBID_CONFIG["bid_rslt_service_key"],
        "resultType": "json",
        "pageNo": 1,
        "numOfRows": 100,
        "cltrMngNo": cltr_mng_no,
    }

    for attempt in range(4):
        if stop_event is not None and stop_event.is_set():
            return "SKIPPED", {}
        try:
            _throttle_request()
            res = requests.get(ONBID_CONFIG["bid_rslt_dtl_url"], params=params, timeout=15)
            if res.status_code == 429:
                time.sleep(1.5 + attempt)
                continue

            raw_text = res.text.lstrip()
            # 공공데이터포털 게이트웨이가 트래픽/TPS 에러 시 XML을 반환하는 경우 처리
            if raw_text.startswith("<"):
                if "returnReasonCode>22<" in raw_text or "LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR" in raw_text:
                    return "QUOTA_EXCEEDED", {"msg": "DAILY_QUOTA_EXCEEDED"}
                if "returnReasonCode>23<" in raw_text or "PER_SECOND" in raw_text:
                    time.sleep(1.5 + attempt)
                    continue
                return "ERROR", {"msg": raw_text[:200]}

            data = res.json()
            res_code = (
                data.get("header", {}).get("resultCode")
                or data.get("result", {}).get("resultCode")
                or ""
            )
            res_msg = (
                data.get("header", {}).get("resultMsg")
                or data.get("result", {}).get("resultMsg")
                or ""
            )

            if res_code == "22":
                return "QUOTA_EXCEEDED", {"msg": res_msg}
            if res_code == "23":
                time.sleep(1.0 + attempt)
                continue
            if res_code == "03":
                return "NODATA", {}
            if res_code != "00":
                return "ERROR", {"code": res_code, "msg": res_msg}

            items = data.get("body", {}).get("items", {}).get("item", [])
            if isinstance(items, dict):
                items = [items]
            if not items:
                return "NODATA", {}

            items_sorted = sorted(
                items,
                key=lambda x: (
                    str(x.get("cltrBidEndDt") or ""),
                    safe_int(x.get("pbctCdtnNo")),
                    safe_int(x.get("pbctNo")),
                ),
                reverse=True,
            )
            latest = items_sorted[0]
            canceled_rounds = [
                it
                for it in items_sorted
                if str(it.get("pbctStatCd") or "") == "0012"
                or bool(str(it.get("afsbRtrcnRsnCont") or "").strip())
            ]

            latest_stat_cd = str(latest.get("pbctStatCd") or "").strip()
            latest_stat_nm = str(
                latest.get("pbctStatNm")
                or ONBID_CONFIG["pbct_stat_codes"].get(latest_stat_cd, "")
            ).strip()
            afsb_rsn = str(latest.get("afsbRtrcnRsnCont") or "").strip()
            rtrcn_rsn = str(latest.get("rtrcnRsnCont") or "").strip()

            past_cancel_note = ""
            if canceled_rounds:
                c_top = canceled_rounds[0]
                c_dt = format_date(c_top.get("cltrOpbdDt") or c_top.get("cltrBidEndDt"))
                c_rsn = str(c_top.get("afsbRtrcnRsnCont") or c_top.get("rtrcnRsnCont") or "").strip()
                past_cancel_note = f"취소이력 {len(canceled_rounds)}회({c_dt}" + (f", {c_rsn})" if c_rsn else ")")

            parsed = {
                "checked_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "pbctNo": str(latest.get("pbctNo") or ""),
                "pbctNsq": str(latest.get("pbctNsq") or ""),
                "pbctsn": str(latest.get("pbctsn") or ""),
                "pbctStatCd": latest_stat_cd,
                "pbctStatNm": latest_stat_nm,
                "scfbAmt": latest.get("scfbAmt"),
                "rtrcnRsnCont": rtrcn_rsn,
                "afsbRtrcnRsnCont": afsb_rsn,
                "cltrBidBgngDt": format_date(latest.get("cltrBidBgngDt")),
                "cltrBidEndDt": format_date(latest.get("cltrBidEndDt")),
                "prptDivNm": str(latest.get("prptDivNm") or ""),
                "dspsMthodNm": str(latest.get("dspsMthodNm") or ""),
                "usgNm": str(latest.get("cltrUsgSclsCtgrNm") or latest.get("cltrUsgMclsCtgrNm") or ""),
                "onbidCltrNm": str(latest.get("onbidCltrNm") or ""),
                "orgNm": str(latest.get("orgNm") or ""),
                "apslEvlAmt": latest.get("apslEvlAmt"),
                "lowstBidPrc": latest.get("lowstBidPrcIndctCont"),
                "past_cancel_note": past_cancel_note,
            }
            return "OK", parsed
        except Exception as e:
            if attempt == 2:
                return "ERROR", {"msg": str(e)}
            time.sleep(0.8)

    return "ERROR", {"msg": "재시도 횟수 초과"}


def classify_disappeared_item(snap_info, rslt_info):
    """
    이탈 물건의 최종 물건상태 라벨과 취소/회수 사유, 낙찰 여부(is_sold)를 반환합니다.
    """
    prev_status = str(snap_info.get("last_status") or "")
    ever_pvct = bool(snap_info.get("ever_pvct")) or ("수의" in prev_status)
    last_seen = snap_info.get("last_seen_date", "")

    if rslt_info.get("_nodata"):
        status_label = "수의계약회수(결과미생성)" if ever_pvct else "개찰전취소(추정)"
        reason = f"개찰결과 없이 목록 제외 (마지막수집: {last_seen})"
        return status_label, reason, False

    stat_cd = str(rslt_info.get("pbctStatCd") or "")
    stat_nm = str(rslt_info.get("pbctStatNm") or "")
    afsb_rsn = str(rslt_info.get("afsbRtrcnRsnCont") or "").strip()
    rtrcn_rsn = str(rslt_info.get("rtrcnRsnCont") or "").strip()
    past_note = str(rslt_info.get("past_cancel_note") or "").strip()

    # 1. 명시적 취소 (0012) 또는 낙찰 후 취소
    if stat_cd == "0012" or stat_nm == "취소" or afsb_rsn:
        status_label = "공매취소(수의후)" if ever_pvct else "공매취소"
        base = afsb_rsn or rtrcn_rsn or "기관 공매취소"
        reason = f"{base} (마지막수집: {last_seen})"
        return status_label, reason, False

    # 2. 낙찰 종결 -> 기존 매물 데이터 추가 대상에서 제외
    if stat_cd == "0010" or stat_nm == "낙찰":
        return "낙찰종결", "낙찰 완료", True

    # 3. 수의계약 가능 상태에서 낙찰 없이 회수/기간만료된 물건
    if ever_pvct or stat_cd == "0009" or stat_nm == "수의계약가능":
        status_label = "수의계약회수"
        detail = "수의계약 미체결 회수/종결"
        if past_note:
            detail += f" [{past_note}]"
        reason = f"{detail} (마지막수집: {last_seen})"
        return status_label, reason, False

    # 4. 일반 유찰 후 재공고/수의전환 없이 회수/보류된 물건
    if stat_cd == "0011" or stat_nm == "유찰":
        status_label = "유찰후회수"
        detail = f"유찰({rtrcn_rsn or '입찰자 없음'}) 후 공매종결/보류"
        if past_note:
            detail += f" [{past_note}]"
        reason = f"{detail} (마지막수집: {last_seen})"
        return status_label, reason, False

    return f"회수/제외({stat_nm or '기타'})", f"{rtrcn_rsn} (마지막수집: {last_seen})".strip(), False


def collect_canceled_and_withdrawn_records(df_live):
    """
    기존 스냅샷 대비 현재 활성 목록(df_live)에서 사라진 물건들을 추적하여,
    낙찰 건을 제외한 '공매취소 / 수의계약회수 / 유찰후회수' 레코드 리스트를 반환합니다.
    반환 포맷은 onbid_crawler.py의 기본 컬럼 구조와 동일합니다.
    """
    items_map = build_historical_snapshot_index()
    active_ids = set()
    if df_live is not None and not df_live.empty and "cltrMngNo" in df_live.columns:
        active_ids = set(df_live["cltrMngNo"].dropna().astype(str).str.strip())

    disappeared = [info for cid, info in items_map.items() if cid not in active_ids]

    # 오늘의 활성 물건도 다음 실행 시 비교할 수 있도록 스냅샷 인덱스에 반영
    update_snapshot_index_from_live_df(items_map, df_live)

    if not disappeared:
        print("[취소/회수 추적] 비교할 과거 이탈 물건이 없습니다.", flush=True)
        return []

    rslt_cache = load_json_file(ONBID_CONFIG["cache_filepath"], {})

    unchecked = []
    for item in disappeared:
        cid = item["cltrMngNo"]
        cached = rslt_cache.get(cid)
        if cached and str(cached.get("checked_at", ""))[:10] >= str(item.get("last_seen_date", "")):
            continue
        unchecked.append(item)

    # 최근 목격일 순 + 수의계약 이력 물건 최우선 조회
    unchecked.sort(key=lambda x: str(x.get("last_seen_date", "")), reverse=True)
    unchecked_pvct = [x for x in unchecked if x.get("ever_pvct")]
    unchecked_other = [x for x in unchecked if not x.get("ever_pvct")]
    prioritized_queue = unchecked_pvct + unchecked_other

    max_calls = ONBID_CONFIG["max_dtl_calls_per_run"]
    target_queue = prioritized_queue[:max_calls]

    print(
        f"[취소/회수 추적] 누적 이탈 물건 {len(disappeared):,}건 중 신규 API 조회: {len(target_queue):,}건 "
        f"(수의계약 이탈 미조회 {len(unchecked_pvct):,}건 우선 / 캐시 보유 {len(rslt_cache):,}건)",
        flush=True,
    )

    if target_queue:
        stop_event = threading.Event()
        completed_cnt = 0
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_item = {
                executor.submit(query_single_bid_rslt_dtl, it["cltrMngNo"], stop_event): it
                for it in target_queue
            }
            for future in as_completed(future_to_item):
                it = future_to_item[future]
                cid = it["cltrMngNo"]
                status_type, payload = future.result()
                if status_type == "SKIPPED":
                    continue
                completed_cnt += 1

                if status_type == "OK":
                    rslt_cache[cid] = payload
                elif status_type == "NODATA":
                    rslt_cache[cid] = {
                        "checked_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "_nodata": True,
                    }
                elif status_type == "QUOTA_EXCEEDED":
                    if not stop_event.is_set():
                        print(
                            "[알림] 입찰결과상세 API 일일 트래픽(1,000건) 도달 -> 캐시된 결과까지 병합합니다.",
                            flush=True,
                        )
                        stop_event.set()

                if completed_cnt % 50 == 0 or completed_cnt == len(target_queue):
                    print(f"  - 취소/회수 상태 확인 진행: {completed_cnt}/{len(target_queue)}건", flush=True)
                    save_json_file(ONBID_CONFIG["cache_filepath"], rslt_cache)

        save_json_file(ONBID_CONFIG["cache_filepath"], rslt_cache)

    # 최근 목격일 순, 수의계약 이력 우선 정렬하여 기존 데이터 하단에 추가할 행 구성
    disappeared.sort(
        key=lambda x: (str(x.get("last_seen_date", "")), 1 if x.get("ever_pvct") else 0),
        reverse=True,
    )

    appended_records = []
    sold_skipped = 0

    for snap in disappeared:
        cid = snap["cltrMngNo"]
        rslt = rslt_cache.get(cid)
        if not rslt:
            continue

        status_label, reason, is_sold = classify_disappeared_item(snap, rslt)
        if is_sold:
            sold_skipped += 1
            continue

        apsl_val = rslt.get("apslEvlAmt") if rslt.get("apslEvlAmt") not in (None, "") else snap.get("apslEvlAmt", 0)
        lowst_val = rslt.get("lowstBidPrc") if rslt.get("lowstBidPrc") not in (None, "") else snap.get("lowstBidPrc", 0)
        bid_rto = snap.get("bidRto", "")
        try:
            a_num = float(str(apsl_val).replace(",", ""))
            l_num = float(str(lowst_val).replace(",", ""))
            if (bid_rto == "" or bid_rto is None) and a_num > 0 and l_num > 0:
                bid_rto = round((l_num / a_num) * 100, 2)
        except Exception:
            pass

        appended_records.append(
            {
                "번호": "",
                "물건관리번호": cid,
                "공고일자": "",
                "등록일자": "",
                "입찰시작일시": rslt.get("cltrBidBgngDt") or format_date(snap.get("bidBgngDt")),
                "입찰마감일시": rslt.get("cltrBidEndDt") or format_date(snap.get("bidEndDt")),
                "재산유형": rslt.get("prptDivNm") or snap.get("prptDivNm", ""),
                "회차": rslt.get("pbctNsq") or snap.get("pbctNsq", ""),
                "차수": rslt.get("pbctsn") or snap.get("pbctsn", ""),
                "공고기관": rslt.get("orgNm") or snap.get("orgNm", ""),
                "용도": rslt.get("usgNm") or snap.get("usgNm", ""),
                "물건명": rslt.get("onbidCltrNm") or snap.get("onbidCltrNm", ""),
                "토지면적(㎡)": snap.get("landSqms", ""),
                "건물면적(㎡)": snap.get("bldSqms", ""),
                "처분방식": rslt.get("dspsMthodNm") or snap.get("dspsMthodNm", ""),
                "소재지": snap.get("addr", ""),
                "최저입찰가(원)": lowst_val,
                "감정가(원)": apsl_val,
                "최저입찰가율(%)": bid_rto,
                "물건상태": status_label,
                "공매번호": rslt.get("pbctNo") or snap.get("pbctNo", ""),
                "취소/회수사유": reason,
            }
        )

    print(
        f"[취소/회수 병합 완료] 추가될 취소·회수 물건: {len(appended_records):,}건 (낙찰종결 제외: {sold_skipped:,}건)",
        flush=True,
    )
    return appended_records
