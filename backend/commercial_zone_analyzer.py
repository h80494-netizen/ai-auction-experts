# -*- coding: utf-8 -*-
"""
단일 도시지역 상업지역(중심·일반·근린·유통상업지역) 폴리곤 정밀 시세·실거래 통합 분석 모듈
- 지도에서 줌인하여 선택한 '특정 1개 상업지역 폴리곤' 내부 데이터만 Point-in-Polygon으로 엄격 분리 추출
- 1) 네이버부동산 매물: 매매 / 전월세(전세·월세) / 환산보증금(보증금 + 월세×100) / 환산보증금 기준 전세가율
- 2) 국토부 실거래가(250m 실거래 격자): 매매 실거래 평당가·건수 / 전월세 실거래·환산보증금 / 실거래 및 교차 전세가율
- 건축연도 기준 3단계 노후도 그룹핑(10년 이내 / 25년 이내 / 25년 이상), 층수군, 면적대 필터 지원
"""

import os
import re
import json
import math
import sqlite3
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

import numpy as np
import pandas as pd
import requests

from naver_price_analyzer import (
    calculate_building_age_info,
    get_age_category_from_text,
    get_area_category_excel,
    get_floor_category_excel,
    get_kakao_address,
)

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "map_data.db")
VWORLD_API_KEY = "8E5DFFF6-C1E4-48F4-83C4-0A49E53D59DE"
VWORLD_DOMAIN = "ai-auction-experts.cloud"

_VWORLD_ZONING_NAME_CACHE: Dict[str, str] = {}
_VWORLD_BBOX_POLY_CACHE: Dict[str, List[Dict[str, Any]]] = {}


def _extract_geometry(geojson_obj: Any) -> Optional[Dict[str, Any]]:
    if not geojson_obj:
        return None
    if isinstance(geojson_obj, str):
        try:
            geojson_obj = json.loads(geojson_obj)
        except Exception:
            return None
    if not isinstance(geojson_obj, dict):
        return None
    if geojson_obj.get("type") == "Feature":
        return geojson_obj.get("geometry")
    if geojson_obj.get("type") in ("Polygon", "MultiPolygon"):
        return geojson_obj
    if "geometry" in geojson_obj and isinstance(geojson_obj["geometry"], dict):
        return geojson_obj["geometry"]
    return None


def _points_in_ring(xs: np.ndarray, ys: np.ndarray, ring: list) -> np.ndarray:
    pts = np.asarray(ring, dtype=float)
    if pts.ndim != 2 or pts.shape[0] < 3:
        return np.zeros(len(xs), dtype=bool)
    x1, y1 = pts[:, 0], pts[:, 1]
    x2, y2 = np.roll(x1, -1), np.roll(y1, -1)
    cond_y = (y1 > ys[:, None]) != (y2 > ys[:, None])
    dy = np.where(np.abs(y2 - y1) < 1e-15, 1e-15, y2 - y1)
    x_intersect = (x2 - x1) * (ys[:, None] - y1) / dy + x1
    crossings = cond_y & (xs[:, None] < x_intersect)
    return (np.count_nonzero(crossings, axis=1) % 2) == 1


def _points_in_polygon_rings(xs: np.ndarray, ys: np.ndarray, rings: list) -> np.ndarray:
    if not rings:
        return np.zeros(len(xs), dtype=bool)
    inside = _points_in_ring(xs, ys, rings[0])
    for hole in rings[1:]:
        if hole:
            inside &= ~_points_in_ring(xs, ys, hole)
    return inside


def points_in_geometry(lons: np.ndarray, lats: np.ndarray, geom: Dict[str, Any]) -> np.ndarray:
    """벡터화된 Point-in-Polygon (Polygon / MultiPolygon 완벽 지원)"""
    n = len(lons)
    if n == 0 or not geom:
        return np.zeros(n, dtype=bool)
    gtype = geom.get("type")
    coords = geom.get("coordinates") or []
    if gtype == "Polygon":
        return _points_in_polygon_rings(lons, lats, coords)
    elif gtype == "MultiPolygon":
        mask = np.zeros(n, dtype=bool)
        for poly_rings in coords:
            mask |= _points_in_polygon_rings(lons, lats, poly_rings)
        return mask
    return np.zeros(n, dtype=bool)


def compute_geometry_bounds_and_area(geom: Dict[str, Any]) -> Tuple[float, float, float, float, float, float, float]:
    """(min_lat, max_lat, min_lng, max_lng, center_lat, center_lng, area_sqm) 산출"""
    all_lons: List[float] = []
    all_lats: List[float] = []

    def _collect_rings(rings: list) -> float:
        if not rings or len(rings[0]) < 3:
            return 0.0
        outer = np.asarray(rings[0], dtype=float)
        all_lons.extend(outer[:, 0].tolist())
        all_lats.extend(outer[:, 1].tolist())
        lat0 = float(np.mean(outer[:, 1]))
        lon0 = float(np.mean(outer[:, 0]))
        m_per_lon = 111320.0 * math.cos(math.radians(lat0))
        m_per_lat = 111132.0

        def _ring_area(r: list) -> float:
            arr = np.asarray(r, dtype=float)
            if arr.ndim != 2 or len(arr) < 3:
                return 0.0
            x = (arr[:, 0] - lon0) * m_per_lon
            y = (arr[:, 1] - lat0) * m_per_lat
            return 0.5 * abs(float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))

        area = _ring_area(rings[0])
        for h in rings[1:]:
            area = max(0.0, area - _ring_area(h))
        return area

    total_area_sqm = 0.0
    gtype = geom.get("type")
    coords = geom.get("coordinates") or []
    if gtype == "Polygon":
        total_area_sqm = _collect_rings(coords)
    elif gtype == "MultiPolygon":
        for poly in coords:
            total_area_sqm += _collect_rings(poly)

    if not all_lats or not all_lons:
        return (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    min_lat, max_lat = min(all_lats), max(all_lats)
    min_lng, max_lng = min(all_lons), max(all_lons)
    center_lat = 0.5 * (min_lat + max_lat)
    center_lng = 0.5 * (min_lng + max_lng)
    return (min_lat, max_lat, min_lng, max_lng, center_lat, center_lng, total_area_sqm)


def fetch_vworld_commercial_polygons_in_bbox(min_lat: float, min_lng: float, max_lat: float, max_lng: float) -> List[Dict[str, Any]]:
    """로컬 zoning_polygons가 없는 지방 도시 등을 위해 V-World LT_C_UQ111 상업지역 폴리곤 조회"""
    cache_key = f"{min_lat:.3f},{min_lng:.3f},{max_lat:.3f},{max_lng:.3f}"
    if cache_key in _VWORLD_BBOX_POLY_CACHE:
        return _VWORLD_BBOX_POLY_CACHE[cache_key]

    results: List[Dict[str, Any]] = []
    try:
        resp = requests.get(
            "https://api.vworld.kr/req/data",
            params={
                "service": "data",
                "request": "GetFeature",
                "data": "LT_C_UQ111",
                "key": VWORLD_API_KEY,
                "domain": VWORLD_DOMAIN,
                "geomFilter": f"BOX({min_lng},{min_lat},{max_lng},{max_lat})",
                "attrFilter": "uname:like:상업",
                "size": "150",
                "crs": "EPSG:4326",
            },
            headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": f"https://{VWORLD_DOMAIN}",
                "Origin": f"https://{VWORLD_DOMAIN}",
            },
            timeout=3.5,
        )
        if resp.status_code == 200:
            data = resp.json()
            feats = (
                data.get("response", {})
                .get("result", {})
                .get("featureCollection", {})
                .get("features", [])
            )
            for idx, f in enumerate(feats):
                geom = f.get("geometry")
                props = f.get("properties") or {}
                uname = props.get("uname") or "상업지역"
                sido = props.get("sido_name") or ""
                sigg = props.get("sigg_name") or ""
                if geom:
                    b = compute_geometry_bounds_and_area(geom)
                    results.append({
                        "id": -(idx + 1),
                        "name": uname,
                        "region_label": f"{sido} {sigg}".strip(),
                        "min_lat": b[0],
                        "max_lat": b[1],
                        "min_lng": b[2],
                        "max_lng": b[3],
                        "geojson": geom,
                    })
    except Exception:
        pass

    _VWORLD_BBOX_POLY_CACHE[cache_key] = results
    return results


def _resolve_detailed_zoning_name(center_lat: float, center_lng: float, fallback_name: str) -> str:
    """'상업지역' 일반 명칭일 경우 V-World LT_C_UQ111로 중심/일반/근린/유통상업지역 세부명 보강"""
    if fallback_name and any(k in fallback_name for k in ["중심상업", "일반상업", "근린상업", "유통상업"]):
        return fallback_name
    key = f"{center_lat:.5f},{center_lng:.5f}"
    if key in _VWORLD_ZONING_NAME_CACHE:
        return _VWORLD_ZONING_NAME_CACHE[key]
    try:
        resp = requests.get(
            "https://api.vworld.kr/req/data",
            params={
                "service": "data",
                "request": "GetFeature",
                "data": "LT_C_UQ111",
                "key": VWORLD_API_KEY,
                "domain": VWORLD_DOMAIN,
                "geomFilter": f"POINT({center_lng} {center_lat})",
                "size": "5",
                "crs": "EPSG:4326",
            },
            headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": f"https://{VWORLD_DOMAIN}",
                "Origin": f"https://{VWORLD_DOMAIN}",
            },
            timeout=2.0,
        )
        if resp.status_code == 200:
            feats = (
                resp.json()
                .get("response", {})
                .get("result", {})
                .get("featureCollection", {})
                .get("features", [])
            )
            for f in feats:
                uname = (f.get("properties") or {}).get("uname") or ""
                if "상업" in uname:
                    _VWORLD_ZONING_NAME_CACHE[key] = uname
                    return uname
    except Exception:
        pass
    _VWORLD_ZONING_NAME_CACHE[key] = fallback_name or "상업지역"
    return _VWORLD_ZONING_NAME_CACHE[key]


def find_commercial_zone_at_point(lat: float, lng: float) -> Optional[Dict[str, Any]]:
    """특정 좌표(주소지)가 속한 단일 도시지역 상업지역 폴리곤 1개를 반환"""
    lon_arr = np.array([float(lng)], dtype=float)
    lat_arr = np.array([float(lat)], dtype=float)

    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            rows = cur.execute(
                """
                SELECT id, name, geojson
                FROM zoning_polygons
                WHERE min_lat <= ? AND max_lat >= ?
                  AND min_lng <= ? AND max_lng >= ?
                  AND name LIKE '%상업%'
                """,
                (lat, lat, lng, lng),
            ).fetchall()
            conn.close()
            for pid, pname, pgeo in rows:
                geom = _extract_geometry(pgeo)
                if geom and bool(points_in_geometry(lon_arr, lat_arr, geom)[0]):
                    detailed_name = _resolve_detailed_zoning_name(lat, lng, pname or "상업지역")
                    return {
                        "polygon_id": int(pid),
                        "zone_name": detailed_name,
                        "geojson": geom,
                    }
        except Exception:
            pass

    # Fallback: V-World LT_C_UQ111
    vw_polys = fetch_vworld_commercial_polygons_in_bbox(lat - 0.005, lng - 0.005, lat + 0.005, lng + 0.005)
    for vp in vw_polys:
        geom = _extract_geometry(vp.get("geojson"))
        if geom and bool(points_in_geometry(lon_arr, lat_arr, geom)[0]):
            return {
                "polygon_id": vp.get("id"),
                "zone_name": vp.get("name") or "상업지역",
                "geojson": geom,
            }
    return None


def filter_df_by_commercial_zones(df: pd.DataFrame, min_lat: float, max_lat: float, min_lng: float, max_lng: float, single_geom: Optional[Dict[str, Any]] = None) -> Tuple[pd.DataFrame, str]:
    """
    DataFrame(위도, 경도 포함)에서 상업지역 폴리곤 내부 매물만 필터링하여 반환.
    - single_geom이 주어지면 오직 해당 단일 상업지역 폴리곤 내부 매물만 추출.
    - single_geom이 없으면 BBox 내 도시지역 상업지역 폴리곤들 내부 매물만 추출.
    """
    if df is None or len(df) == 0:
        return df, ""

    lons = df["경도"].to_numpy(dtype=float)
    lats = df["위도"].to_numpy(dtype=float)

    if single_geom:
        geom = _extract_geometry(single_geom)
        if not geom:
            return df.iloc[0:0].copy(), "유효하지 않은 상업지역 폴리곤"
        mask = points_in_geometry(lons, lats, geom)
        filtered = df[mask].copy()
        return filtered, "선택 단일 상업지역 폴리곤 내 매물 전용"

    polys: List[Tuple[str, Dict[str, Any]]] = []
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            rows = cur.execute(
                """
                SELECT name, geojson
                FROM zoning_polygons
                WHERE max_lat >= ? AND min_lat <= ?
                  AND max_lng >= ? AND min_lng <= ?
                  AND name LIKE '%상업%'
                """,
                (min_lat, max_lat, min_lng, max_lng),
            ).fetchall()
            conn.close()
            for r_name, r_geo in rows:
                g = _extract_geometry(r_geo)
                if g:
                    polys.append((r_name or "상업지역", g))
        except Exception:
            pass

    if not polys:
        for vp in fetch_vworld_commercial_polygons_in_bbox(min_lat, min_lng, max_lat, max_lng):
            g = _extract_geometry(vp.get("geojson"))
            if g:
                polys.append((vp.get("name") or "상업지역", g))

    if not polys:
        return df.iloc[0:0].copy(), "반경 내 도시지역 상업지역 폴리곤 없음"

    combined_mask = np.zeros(len(df), dtype=bool)
    zone_labels = np.array([""] * len(df), dtype=object)
    for z_name, g in polys:
        m = points_in_geometry(lons, lats, g)
        newly = m & (~combined_mask)
        zone_labels[newly] = z_name
        combined_mask |= m

    filtered = df[combined_mask].copy()
    filtered["zoning_label"] = zone_labels[combined_mask]
    return filtered, f"도시지역 상업지역 폴리곤({len(polys)}개 구역) 내 매물 전용"


def _load_polygon_from_request(polygon_id: Optional[int], geojson_input: Any, zone_name: Optional[str]) -> Tuple[Optional[Dict[str, Any]], str, Optional[int]]:
    geom = _extract_geometry(geojson_input) if geojson_input else None
    resolved_name = zone_name or "상업지역"
    resolved_id = polygon_id

    if geom is None and polygon_id is not None and polygon_id > 0 and os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        row = cur.execute("SELECT id, name, geojson FROM zoning_polygons WHERE id = ?", (int(polygon_id),)).fetchone()
        conn.close()
        if row:
            resolved_id = int(row[0])
            resolved_name = row[1] or resolved_name
            geom = _extract_geometry(row[2])

    return geom, resolved_name, resolved_id


def analyze_commercial_zone(
    polygon_id: Optional[int] = None,
    geojson_input: Any = None,
    zone_name: Optional[str] = None,
    property_type: str = "상가",
    age_group: str = "전체",
    floor_group: str = "전체",
    area_group: str = "전체",
    target_pyeong: float = 25.0,
) -> Dict[str, Any]:
    """
    선택된 단일 상업지역 폴리곤 1개에 대한 종합 분석:
    1) 네이버부동산 매물: 매매 / 전월세 / 환산보증금(보증금 + 월세×100) / 환산보증금 기준 전세가율 + 매물 리스트
    2) 국토교통부 실거래가(250m 격자): 매매 실거래 / 전월세 실거래 / 환산보증금·실거래 전세가율 / 신축·구축 평당가
    """
    geom, raw_zone_name, resolved_id = _load_polygon_from_request(polygon_id, geojson_input, zone_name)
    if not geom:
        return {"error": "선택된 상업지역 폴리곤 도형 정보를 찾을 수 없습니다."}

    min_lat, max_lat, min_lng, max_lng, center_lat, center_lng, area_sqm = compute_geometry_bounds_and_area(geom)
    detailed_zone_name = _resolve_detailed_zoning_name(center_lat, center_lng, raw_zone_name)
    zone_area_pyeong = round(area_sqm / 3.305785, 0)

    if not os.path.exists(DB_PATH):
        return {"error": "데이터베이스 파일을 찾을 수 없습니다."}

    conn = sqlite3.connect(DB_PATH)

    # ------------------------------------------------------------------
    # PART 1: 네이버부동산 매물 분석 (선택 상업지역 폴리곤 내부 엄격 필터링)
    # ------------------------------------------------------------------
    ptype = (property_type or "상가").strip()
    if ptype in ("전체", "ALL"):
        naver_type_cond = "1=1"
    elif "아파트" in ptype:
        naver_type_cond = "estate_type = '아파트'"
    elif any(k in ptype for k in ["빌라", "다세대", "연립"]):
        naver_type_cond = "(estate_type LIKE '%다세대%' OR estate_type LIKE '%빌라%')"
    elif "오피스텔" in ptype:
        naver_type_cond = "estate_type LIKE '%오피스텔%'"
    elif any(k in ptype for k in ["단독", "다가구"]):
        naver_type_cond = "estate_type LIKE '%단독%'"
    elif "토지" in ptype:
        naver_type_cond = "estate_type LIKE '%토지%'"
    else:
        naver_type_cond = "(estate_type LIKE '%상가%' OR estate_type LIKE '%근린%')"

    naver_sql = f"""
        SELECT address, price, rent, floor, area, deal_type, type_detail, lat, lng, estate_type, age_info
        FROM naver_real_estate
        WHERE ({naver_type_cond})
          AND lat >= ? AND lat <= ?
          AND lng >= ? AND lng <= ?
    """
    ndf = pd.read_sql_query(naver_sql, conn, params=[min_lat, max_lat, min_lng, max_lng])

    if not ndf.empty:
        in_poly = points_in_geometry(
            ndf["lng"].to_numpy(dtype=float),
            ndf["lat"].to_numpy(dtype=float),
            geom,
        )
        ndf = ndf[in_poly].copy()

    # 전체 상업지역 내 유형별 매물 분포(상단 요약용 - 필터 전 스냅샷)
    all_types_sql = """
        SELECT estate_type, deal_type, lat, lng
        FROM naver_real_estate
        WHERE lat >= ? AND lat <= ? AND lng >= ? AND lng <= ?
    """
    all_tdf = pd.read_sql_query(all_types_sql, conn, params=[min_lat, max_lat, min_lng, max_lng])
    type_counts_in_zone: Dict[str, int] = {}
    if not all_tdf.empty:
        in_p_all = points_in_geometry(
            all_tdf["lng"].to_numpy(dtype=float),
            all_tdf["lat"].to_numpy(dtype=float),
            geom,
        )
        all_tdf = all_tdf[in_p_all]
        for et, cnt in all_tdf["estate_type"].value_counts().items():
            type_counts_in_zone[str(et)] = int(cnt)

    is_housing_like = any(k in ptype for k in ["아파트", "빌라", "다세대", "연립", "단독", "다가구", "오피스텔"])
    is_land_like = "토지" in ptype or "대지" in ptype

    age_breakdown_summary = {
        "10년 이내": {"sale_count": 0, "rent_count": 0, "avg_sale_pp": 0.0, "avg_conv_pp": 0.0, "jeonse_ratio": 0.0},
        "25년 이내": {"sale_count": 0, "rent_count": 0, "avg_sale_pp": 0.0, "avg_conv_pp": 0.0, "jeonse_ratio": 0.0},
        "25년 이상": {"sale_count": 0, "rent_count": 0, "avg_sale_pp": 0.0, "avg_conv_pp": 0.0, "jeonse_ratio": 0.0},
    }
    ndf_all_zone = pd.DataFrame()

    def _normalize_area_filter_code(ag_val: str) -> str:
        if not ag_val or ag_val == "전체":
            return "전체"
        s = str(ag_val).replace(" ", "")
        if s == "소" or "소(" in s or "15평이하" in s:
            return "소"
        if s == "대" or "대(" in s or "30평이상" in s or "30평초과" in s:
            return "대"
        if s == "중" or "중(" in s or "30평이하" in s:
            return "중"
        return ag_val

    def _apply_floor_filter(sub_df: pd.DataFrame, fg_val: str) -> pd.DataFrame:
        if sub_df.empty or not fg_val or fg_val == "전체":
            return sub_df
        if fg_val == "2층이상":
            return sub_df[sub_df["floor_group_label"].isin(["저", "중", "고"])]
        return sub_df[sub_df["floor_group_label"] == fg_val]

    def _apply_area_filter(sub_df: pd.DataFrame, ag_val: str) -> pd.DataFrame:
        code = _normalize_area_filter_code(ag_val)
        if sub_df.empty or code == "전체":
            return sub_df
        if code in ("소", "중", "대"):
            return sub_df[sub_df["area_group_code"] == code]
        return sub_df

    representative_address = get_kakao_address(center_lat, center_lng) or ""

    if not ndf.empty:
        # 카카오 역지오코딩 실패 시 유효 지번/도로명 주소 보조 추출
        if not representative_address:
            valid_addrs = [
                str(a).strip() for a in ndf["address"].dropna().tolist()
                if str(a).strip() and any(ch.isdigit() for ch in str(a))
            ]
            if valid_addrs:
                representative_address = valid_addrs[0]

        area_m2 = pd.to_numeric(ndf["area"], errors="coerce")
        ndf["pyeong"] = (area_m2 / 3.305785).round(2)
        ap = ndf["pyeong"]
        # 평수 소·중·대 3구분: 소(15평 이하) / 중(30평 이하) / 대(30평 이상)
        ndf["area_group_code"] = np.select(
            [ap.isna(), ap <= 15.0, ap <= 30.0],
            ["중", "소", "중"],
            default="대",
        )
        ndf["area_group_label"] = np.select(
            [ndf["area_group_code"] == "소", ndf["area_group_code"] == "중"],
            ["소 (15평 이하)", "중 (30평 이하)"],
            default="대 (30평 이상)",
        )

        fl_nums, fl_totals = [], []
        for raw_fl in ndf["floor"].tolist():
            f_str = str(raw_fl or "")
            if "/" in f_str:
                p0, p1 = f_str.split("/", 1)
                fl_nums.append(p0.strip())
                fl_totals.append(p1.strip())
            else:
                fl_nums.append(f_str.strip())
                fl_totals.append("")
        ndf["floor_cat"] = [
            "-" if is_land_like else get_floor_category_excel(fn, tf, is_housing=is_housing_like)
            for fn, tf in zip(fl_nums, fl_totals)
        ]
        fc_series = ndf["floor_cat"].astype(str)
        ndf["floor_group_label"] = np.where(
            fc_series.str.startswith("B"),
            "지하",
            np.where(fc_series.isin(["1층", "저", "중", "고", "-"]), fc_series, "저"),
        )

        ndf["age_cat"] = [get_age_category_from_text(x) for x in ndf["age_info"].tolist()]
        ndf["age_group_label"] = np.select(
            [ndf["age_cat"] == 10, ndf["age_cat"] == 25],
            ["10년 이내", "25년 이내"],
            default="25년 이상",
        )

        p_num = pd.to_numeric(
            ndf["price"].astype(str).str.replace(",", "", regex=False).str.strip(),
            errors="coerce",
        )
        dep_man = np.where(p_num > 1000000, p_num / 10000.0, p_num)
        r_num = pd.to_numeric(
            ndf["rent"].astype(str).str.replace(",", "", regex=False).str.replace("만", "", regex=False).str.strip(),
            errors="coerce",
        ).fillna(0.0)
        r_num = np.where(r_num > 0, r_num, 0.0)

        deal_s = ndf["deal_type"].fillna("").astype(str).str.strip()
        is_rental = (r_num > 0) | deal_s.isin(["월세", "전세", "전월세", "단기임대"])
        is_sale = deal_s.str.contains("매매", na=False) & (~is_rental)

        ndf["deposit_man"] = dep_man
        ndf["rent_man"] = r_num
        # 환산보증금(만원) = 보증금(만원) + 월세(만원) * 100
        ndf["conv_deposit_man"] = np.where(is_rental, dep_man + (r_num * 100.0), dep_man)
        ndf["is_sale"] = is_sale
        ndf["is_rental"] = is_rental
        ndf["pyeong_price"] = np.where(ndf["pyeong"] > 0, ndf["conv_deposit_man"] / ndf["pyeong"], np.nan)
        ndf = ndf[(ndf["conv_deposit_man"] > 0) & (ndf["pyeong"] > 0)].copy()
        ndf_all_zone = ndf.copy()

        # 노후도 그룹별 요약 (층수/면적 필터만 적용된 상태에서 3대 노후도 비교 제공)
        base_for_age = _apply_area_filter(_apply_floor_filter(ndf, floor_group), area_group)
        for g_label in ("10년 이내", "25년 이내", "25년 이상"):
            sub_g = base_for_age[base_for_age["age_group_label"] == g_label]
            sub_s = sub_g[sub_g["is_sale"]]
            sub_r = sub_g[sub_g["is_rental"]]
            s_pp = float(sub_s["pyeong_price"].dropna().mean()) if len(sub_s) > 0 else 0.0
            r_pp = float(sub_r["pyeong_price"].dropna().mean()) if len(sub_r) > 0 else 0.0
            j_rat = round((r_pp / s_pp) * 100.0, 1) if (s_pp > 0 and r_pp > 0) else 0.0
            age_breakdown_summary[g_label] = {
                "sale_count": int(len(sub_s)),
                "rent_count": int(len(sub_r)),
                "avg_sale_pp": round(s_pp, 1),
                "avg_conv_pp": round(r_pp, 1),
                "jeonse_ratio": j_rat,
            }

        # 세부 조건 필터링 적용 (노후도 / 층수 / 평수 소·중·대)
        if age_group and age_group in ("10년 이내", "25년 이내", "25년 이상"):
            ndf = ndf[ndf["age_group_label"] == age_group]
        ndf = _apply_floor_filter(ndf, floor_group)
        ndf = _apply_area_filter(ndf, area_group)

    # 네이버 매매 vs 전월세 집계
    naver_sale_items: List[Dict[str, Any]] = []
    naver_rent_items: List[Dict[str, Any]] = []

    if not ndf.empty:
        sale_df = ndf[ndf["is_sale"]].copy()
        rent_df = ndf[ndf["is_rental"]].copy()

        naver_sale_cnt = int(len(sale_df))
        naver_rent_cnt = int(len(rent_df))
        jeonse_only_cnt = int((rent_df["deal_type"].astype(str).str.strip() == "전세").sum()) if naver_rent_cnt > 0 else 0
        wolse_only_cnt = naver_rent_cnt - jeonse_only_cnt

        avg_sale_price_man = float(sale_df["deposit_man"].mean()) if naver_sale_cnt > 0 else 0.0
        avg_sale_pp = float(sale_df["pyeong_price"].dropna().mean()) if naver_sale_cnt > 0 else 0.0
        median_sale_pp = float(sale_df["pyeong_price"].dropna().median()) if naver_sale_cnt > 0 else 0.0

        avg_rent_dep_man = float(rent_df["deposit_man"].mean()) if naver_rent_cnt > 0 else 0.0
        avg_rent_monthly_man = float(rent_df["rent_man"].mean()) if naver_rent_cnt > 0 else 0.0
        avg_conv_dep_man = float(rent_df["conv_deposit_man"].mean()) if naver_rent_cnt > 0 else 0.0
        avg_conv_pp = float(rent_df["pyeong_price"].dropna().mean()) if naver_rent_cnt > 0 else 0.0
        median_conv_pp = float(rent_df["pyeong_price"].dropna().median()) if naver_rent_cnt > 0 else 0.0

        # 환산보증금 기준 전세가율 (%)
        naver_jeonse_ratio_asking = (avg_conv_pp / avg_sale_pp * 100.0) if (avg_sale_pp > 0 and avg_conv_pp > 0) else 0.0
        naver_jeonse_ratio_est90 = (avg_conv_pp / (avg_sale_pp * 0.9) * 100.0) if (avg_sale_pp > 0 and avg_conv_pp > 0) else 0.0

        for _, r in sale_df.sort_values(by="pyeong_price", ascending=False).head(80).iterrows():
            ai = calculate_building_age_info(r.get("age_info", ""))
            naver_sale_items.append({
                "address": str(r.get("address") or "")[:36],
                "type_detail": str(r.get("type_detail") or r.get("estate_type") or ""),
                "deal_type": str(r.get("deal_type") or "매매"),
                "floor": str(r.get("floor") or "-"),
                "floor_cat": str(r.get("floor_cat") or "-"),
                "floor_group": str(r.get("floor_group_label") or "-"),
                "area_group": str(r.get("area_group_label") or "-"),
                "pyeong": round(float(r.get("pyeong") or 0), 1),
                "price_man": round(float(r.get("deposit_man") or 0), 0),
                "price_eon": round(float(r.get("deposit_man") or 0) / 10000.0, 2),
                "pyeong_price": round(float(r.get("pyeong_price") or 0), 1),
                "age_category": ai["category_label"],
                "age_display": ai["display"],
                "age_badge_color": ai["badge_color"],
            })

        for _, r in rent_df.sort_values(by="pyeong_price", ascending=False).head(80).iterrows():
            ai = calculate_building_age_info(r.get("age_info", ""))
            dep_m = round(float(r.get("deposit_man") or 0), 0)
            mon_m = round(float(r.get("rent_man") or 0), 1)
            conv_m = round(float(r.get("conv_deposit_man") or 0), 0)
            naver_rent_items.append({
                "address": str(r.get("address") or "")[:36],
                "type_detail": str(r.get("type_detail") or r.get("estate_type") or ""),
                "deal_type": str(r.get("deal_type") or "월세"),
                "floor": str(r.get("floor") or "-"),
                "floor_cat": str(r.get("floor_cat") or "-"),
                "floor_group": str(r.get("floor_group_label") or "-"),
                "area_group": str(r.get("area_group_label") or "-"),
                "pyeong": round(float(r.get("pyeong") or 0), 1),
                "deposit_man": dep_m,
                "rent_man": mon_m,
                "conv_deposit_man": conv_m,
                "conv_deposit_eon": round(conv_m / 10000.0, 2),
                "conv_pyeong_price": round(float(r.get("pyeong_price") or 0), 1),
                "age_category": ai["category_label"],
                "age_display": ai["display"],
                "age_badge_color": ai["badge_color"],
            })
    else:
        naver_sale_cnt = naver_rent_cnt = jeonse_only_cnt = wolse_only_cnt = 0
        avg_sale_price_man = avg_sale_pp = median_sale_pp = 0.0
        avg_rent_dep_man = avg_rent_monthly_man = avg_conv_dep_man = avg_conv_pp = median_conv_pp = 0.0
        naver_jeonse_ratio_asking = naver_jeonse_ratio_est90 = 0.0

    # ------------------------------------------------------------------
    # PART 2: 국토교통부 실거래가 분석 (선택 상업지역 폴리곤 내부 250m 격자 정밀 매칭)
    # ------------------------------------------------------------------
    # 250m 격자 중심점 또는 격자 셀(±0.001125 lat, ±0.0014 lng)의 꼭짓점이 폴리곤과 교차하는 격자 추출
    pad_lat = 0.0012
    pad_lng = 0.0015
    rp_sql = """
        SELECT property_type, lat, lng, avg_price_per_pyeong, avg_deposit_per_pyeong, avg_rent,
               jeonse_ratio, transaction_count, sale_count, rent_count,
               sales_count_under_10, sales_count_10_to_20, sales_count_20_to_30, sales_count_over_30,
               sale_price_change_rate, rent_price_change_rate, new_build_price, old_build_price
        FROM realprice_grids
        WHERE lat >= ? AND lat <= ? AND lng >= ? AND lng <= ?
    """
    rpdf = pd.read_sql_query(
        rp_sql,
        conn,
        params=[min_lat - pad_lat, max_lat + pad_lat, min_lng - pad_lng, max_lng + pad_lng],
    )
    conn.close()

    if not rpdf.empty:
        glons = rpdf["lng"].to_numpy(dtype=float)
        glats = rpdf["lat"].to_numpy(dtype=float)
        # 1차: 격자 중심점이 상업지역 폴리곤 내부인 경우
        g_mask = points_in_geometry(glons, glats, geom)
        # 2차: 좁고 긴 노선형 상업지역일 경우 격자 4분면 샘플링 교차 판정
        if not g_mask.any():
            for d_la, d_ln in [(-0.0008, -0.001), (-0.0008, 0.001), (0.0008, -0.001), (0.0008, 0.001)]:
                g_mask |= points_in_geometry(glons + d_ln, glats + d_la, geom)
        rpdf = rpdf[g_mask].copy()

    def _agg_realprice_subset(sub: pd.DataFrame) -> Dict[str, Any]:
        if sub is None or sub.empty:
            return {
                "grid_count": 0,
                "sale_count": 0,
                "rent_count": 0,
                "avg_sale_pyeong_price": 0.0,
                "avg_deposit_pyeong_price": 0.0,
                "avg_monthly_rent": 0.0,
                "conv_deposit_pyeong_price": 0.0,
                "jeonse_ratio": 0.0,
                "new_build_pyeong_price": 0.0,
                "old_build_pyeong_price": 0.0,
                "age_tx_counts": {"10년 이내": 0, "25년 이내": 0, "25년 이상": 0},
            }

        s_sub = sub[(sub["sale_count"] > 0) & (sub["avg_price_per_pyeong"] > 0)]
        r_sub = sub[sub["rent_count"] > 0]

        tot_sale_cnt = int(sub["sale_count"].fillna(0).sum())
        tot_rent_cnt = int(sub["rent_count"].fillna(0).sum())

        if not s_sub.empty and s_sub["sale_count"].sum() > 0:
            w_sale_pp = float(np.average(s_sub["avg_price_per_pyeong"], weights=s_sub["sale_count"]))
        elif not s_sub.empty:
            w_sale_pp = float(s_sub["avg_price_per_pyeong"].mean())
        else:
            w_sale_pp = 0.0

        if not r_sub.empty and r_sub["rent_count"].sum() > 0:
            r_valid_dep = r_sub[r_sub["avg_deposit_per_pyeong"] > 0]
            w_dep_pp = (
                float(np.average(r_valid_dep["avg_deposit_per_pyeong"], weights=r_valid_dep["rent_count"]))
                if not r_valid_dep.empty and r_valid_dep["rent_count"].sum() > 0
                else 0.0
            )
            w_rent = float(np.average(r_sub["avg_rent"].fillna(0), weights=r_sub["rent_count"]))
            jr_valid = r_sub[r_sub["jeonse_ratio"] > 0]
            w_jr = (
                float(np.average(jr_valid["jeonse_ratio"], weights=jr_valid["rent_count"]))
                if not jr_valid.empty and jr_valid["rent_count"].sum() > 0
                else 0.0
            )
        else:
            w_dep_pp = 0.0
            w_rent = 0.0
            w_jr = 0.0

        # avg_deposit_per_pyeong이 이미 환산보증금 평당가 또는 전세보증금 평당가로 구축되어 있으며,
        # jeonse_ratio가 0일 때 w_dep_pp / w_sale_pp 로 보완 계산
        conv_pp = w_dep_pp
        if w_jr <= 0 and w_sale_pp > 0 and conv_pp > 0:
            w_jr = (conv_pp / w_sale_pp) * 100.0

        nb_sub = sub[sub["new_build_price"] > 0]
        ob_sub = sub[sub["old_build_price"] > 0]
        nb_pp = float(nb_sub["new_build_price"].mean()) if not nb_sub.empty else 0.0
        ob_pp = float(ob_sub["old_build_price"].mean()) if not ob_sub.empty else 0.0

        u10 = int(sub["sales_count_under_10"].fillna(0).sum())
        c10_20 = int(sub["sales_count_10_to_20"].fillna(0).sum())
        c20_30 = int(sub["sales_count_20_to_30"].fillna(0).sum())
        o30 = int(sub["sales_count_over_30"].fillna(0).sum())

        return {
            "grid_count": int(len(sub)),
            "sale_count": tot_sale_cnt,
            "rent_count": tot_rent_cnt,
            "avg_sale_pyeong_price": round(w_sale_pp, 1),
            "avg_deposit_pyeong_price": round(w_dep_pp, 1),
            "avg_monthly_rent": round(w_rent, 1),
            "conv_deposit_pyeong_price": round(conv_pp, 1),
            "jeonse_ratio": round(w_jr, 1),
            "new_build_pyeong_price": round(nb_pp, 1),
            "old_build_pyeong_price": round(ob_pp, 1),
            "age_tx_counts": {
                "10년 이내": u10,
                "25년 이내": c10_20 + int(round(c20_30 * 0.5)),
                "25년 이상": o30 + (c20_30 - int(round(c20_30 * 0.5))),
            },
        }

    # 선택 물건 유형에 대응하는 실거래가 매칭
    if ptype in ("전체", "ALL"):
        rp_target_df = rpdf
    elif "아파트" in ptype:
        rp_target_df = rpdf[rpdf["property_type"] == "아파트"] if not rpdf.empty else rpdf
    elif any(k in ptype for k in ["빌라", "다세대", "연립"]):
        rp_target_df = rpdf[rpdf["property_type"] == "다세대"] if not rpdf.empty else rpdf
    elif "오피스텔" in ptype:
        rp_target_df = rpdf[rpdf["property_type"] == "오피스텔"] if not rpdf.empty else rpdf
    elif any(k in ptype for k in ["단독", "다가구"]):
        rp_target_df = rpdf[rpdf["property_type"] == "단독"] if not rpdf.empty else rpdf
    elif "토지" in ptype:
        rp_target_df = rpdf[rpdf["property_type"] == "토지"] if not rpdf.empty else rpdf
    else:
        rp_target_df = rpdf[rpdf["property_type"].isin(["상가(집합)", "상가(일반)"])] if not rpdf.empty else rpdf

    rp_primary = _agg_realprice_subset(rp_target_df)

    # 상가 선택 시: 집합상가 / 일반상가 분리 집계 + 동 상업지역 오피스텔(준주거·업무임대 지표) 보조 집계 + 교차 전세가율 산출
    rp_sangga_jiphap = _agg_realprice_subset(rpdf[rpdf["property_type"] == "상가(집합)"]) if not rpdf.empty else _agg_realprice_subset(None)
    rp_sangga_ilban = _agg_realprice_subset(rpdf[rpdf["property_type"] == "상가(일반)"]) if not rpdf.empty else _agg_realprice_subset(None)
    rp_officetel_bench = _agg_realprice_subset(rpdf[rpdf["property_type"] == "오피스텔"]) if not rpdf.empty else _agg_realprice_subset(None)

    # 노후도 선택 시 실거래 평당가 보정값(신축/구축 실거래 지표 반영)
    selected_rp_sale_pp = rp_primary["avg_sale_pyeong_price"]
    if age_group == "10년 이내" and rp_primary["new_build_pyeong_price"] > 0:
        selected_rp_sale_pp = rp_primary["new_build_pyeong_price"]
    elif age_group == "25년 이상" and rp_primary["old_build_pyeong_price"] > 0:
        selected_rp_sale_pp = rp_primary["old_build_pyeong_price"]

    # 상가 교차 전세가율: (네이버 환산보증금 평당가 ÷ 국토부 실거래 매매 평당가) × 100
    cross_jeonse_ratio = (
        round((avg_conv_pp / selected_rp_sale_pp) * 100.0, 1)
        if (avg_conv_pp > 0 and selected_rp_sale_pp > 0)
        else 0.0
    )
    cross_jeonse_ratio_median = (
        round((median_conv_pp / selected_rp_sale_pp) * 100.0, 1)
        if (median_conv_pp > 0 and selected_rp_sale_pp > 0)
        else 0.0
    )

    # 기준 평수(예: 25평) 환산 시세 비교 요약
    ref_pyeong = float(target_pyeong) if target_pyeong and target_pyeong > 0 else 25.0

    # ------------------------------------------------------------------
    # PART 3: 다차원 그룹핑 비교표 산출
    #   - 층수(1층 / 지하 / 저 / 중 / 고)
    #   - 건축년도(10년 이내 / 25년 이내 / 25년 이상)
    #   - 평수 소·중·대(소: 15평 이하 / 중: 30평 이하 / 대: 30평 이상)
    #   - 복합 매트릭스(층수 × 건축년도 × 평수 소·중·대)
    # ------------------------------------------------------------------
    group_comparisons: Dict[str, Any] = {
        "by_floor": [],
        "by_age": [],
        "by_area": [],
        "matrix_3d": [],
    }
    if not ndf_all_zone.empty and not is_land_like:
        floor_order = ["저", "중", "고", "지하"] if is_housing_like else ["1층", "지하", "저", "중", "고"]
        age_order = ["10년 이내", "25년 이내", "25년 이상"]
        area_order = [
            ("소", "소 (15평 이하)"),
            ("중", "중 (30평 이하)"),
            ("대", "대 (30평 이상)"),
        ]

        def _rp_bench_pp(ag_lbl: Optional[str] = None) -> float:
            if ag_lbl == "10년 이내" and rp_primary["new_build_pyeong_price"] > 0:
                return float(rp_primary["new_build_pyeong_price"])
            if ag_lbl == "25년 이상" and rp_primary["old_build_pyeong_price"] > 0:
                return float(rp_primary["old_build_pyeong_price"])
            return float(rp_primary["avg_sale_pyeong_price"] or 0.0)

        def _build_group_stats(sub_g: pd.DataFrame, ag_for_rp: Optional[str] = None) -> Dict[str, Any]:
            if sub_g.empty:
                return {
                    "sale_count": 0,
                    "avg_sale_pp": 0.0,
                    "median_sale_pp": 0.0,
                    "rent_count": 0,
                    "jeonse_count": 0,
                    "wolse_count": 0,
                    "avg_deposit_man": 0.0,
                    "avg_rent_man": 0.0,
                    "avg_conv_deposit_man": 0.0,
                    "avg_conv_pp": 0.0,
                    "median_conv_pp": 0.0,
                    "jeonse_ratio_asking": 0.0,
                    "jeonse_ratio_est90": 0.0,
                    "cross_jeonse_ratio_realprice": 0.0,
                }
            s_rows = sub_g[sub_g["is_sale"]]
            r_rows = sub_g[sub_g["is_rental"]]
            sc = int(len(s_rows))
            rc = int(len(r_rows))
            j_cnt = int((r_rows["deal_type"].astype(str).str.strip() == "전세").sum()) if rc > 0 else 0
            w_cnt = rc - j_cnt
            s_pp = float(s_rows["pyeong_price"].dropna().mean()) if sc > 0 else 0.0
            s_med = float(s_rows["pyeong_price"].dropna().median()) if sc > 0 else 0.0
            r_pp = float(r_rows["pyeong_price"].dropna().mean()) if rc > 0 else 0.0
            r_med = float(r_rows["pyeong_price"].dropna().median()) if rc > 0 else 0.0
            dep_m = float(r_rows["deposit_man"].mean()) if rc > 0 else 0.0
            mon_m = float(r_rows["rent_man"].mean()) if rc > 0 else 0.0
            conv_m = float(r_rows["conv_deposit_man"].mean()) if rc > 0 else 0.0
            jr_ask = round((r_pp / s_pp) * 100.0, 1) if (s_pp > 0 and r_pp > 0) else 0.0
            jr_90 = round((r_pp / (s_pp * 0.9)) * 100.0, 1) if (s_pp > 0 and r_pp > 0) else 0.0
            rp_pp = _rp_bench_pp(ag_for_rp)
            cross_jr = round((r_pp / rp_pp) * 100.0, 1) if (r_pp > 0 and rp_pp > 0) else 0.0
            return {
                "sale_count": sc,
                "avg_sale_pp": round(s_pp, 1),
                "median_sale_pp": round(s_med, 1),
                "rent_count": rc,
                "jeonse_count": j_cnt,
                "wolse_count": w_cnt,
                "avg_deposit_man": round(dep_m, 0),
                "avg_rent_man": round(mon_m, 1),
                "avg_conv_deposit_man": round(conv_m, 0),
                "avg_conv_pp": round(r_pp, 1),
                "median_conv_pp": round(r_med, 1),
                "jeonse_ratio_asking": jr_ask,
                "jeonse_ratio_est90": jr_90,
                "cross_jeonse_ratio_realprice": cross_jr,
            }

        # 1) 층수별 비교 (선택된 건축년도·평수 필터 반영)
        base_fl = ndf_all_zone.copy()
        if age_group and age_group in ("10년 이내", "25년 이내", "25년 이상"):
            base_fl = base_fl[base_fl["age_group_label"] == age_group]
        base_fl = _apply_area_filter(base_fl, area_group)
        for fg in floor_order:
            st = _build_group_stats(base_fl[base_fl["floor_group_label"] == fg], age_group if age_group != "전체" else None)
            group_comparisons["by_floor"].append({"group": fg, "code": fg, **st})

        # 2) 건축년도별 비교 (선택된 층수·평수 필터 반영)
        base_ag = _apply_area_filter(_apply_floor_filter(ndf_all_zone, floor_group), area_group)
        for ag in age_order:
            st = _build_group_stats(base_ag[base_ag["age_group_label"] == ag], ag)
            group_comparisons["by_age"].append({"group": ag, "code": ag, **st})

        # 3) 평수(소·중·대)별 비교 (선택된 층수·건축년도 필터 반영)
        base_ar = _apply_floor_filter(ndf_all_zone, floor_group)
        if age_group and age_group in ("10년 이내", "25년 이내", "25년 이상"):
            base_ar = base_ar[base_ar["age_group_label"] == age_group]
        for ar_code, ar_lbl in area_order:
            st = _build_group_stats(base_ar[base_ar["area_group_code"] == ar_code], age_group if age_group != "전체" else None)
            group_comparisons["by_area"].append({"group": ar_lbl, "code": ar_code, **st})

        # 4) 복합 3축 매트릭스 (층수 × 건축년도 × 평수 소·중·대) — 폴리곤 내부 전체 조합 일람
        for fg in floor_order:
            sub_f = ndf_all_zone[ndf_all_zone["floor_group_label"] == fg]
            if sub_f.empty:
                continue
            for ag in age_order:
                sub_fa = sub_f[sub_f["age_group_label"] == ag]
                if sub_fa.empty:
                    continue
                for ar_code, ar_lbl in area_order:
                    sub_faa = sub_fa[sub_fa["area_group_code"] == ar_code]
                    if sub_faa.empty:
                        continue
                    st = _build_group_stats(sub_faa, ag)
                    if st["sale_count"] == 0 and st["rent_count"] == 0:
                        continue
                    group_comparisons["matrix_3d"].append({
                        "floor_group": fg,
                        "age_group": ag,
                        "area_code": ar_code,
                        "area_label": ar_lbl,
                        **st,
                    })

    return {
        "zone_info": {
            "polygon_id": resolved_id,
            "zone_name": detailed_zone_name,
            "raw_zone_name": raw_zone_name,
            "representative_address": representative_address,
            "center_lat": round(center_lat, 6),
            "center_lng": round(center_lng, 6),
            "area_sqm": round(area_sqm, 0),
            "area_pyeong": int(zone_area_pyeong),
            "naver_type_counts": type_counts_in_zone,
        },
        "filters_applied": {
            "property_type": ptype,
            "age_group": age_group,
            "floor_group": floor_group,
            "area_group": _normalize_area_filter_code(area_group),
            "ref_pyeong": ref_pyeong,
        },
        "naver_analysis": {
            "sale_count": naver_sale_cnt,
            "rent_count": naver_rent_cnt,
            "jeonse_count": jeonse_only_cnt,
            "wolse_count": wolse_only_cnt,
            "avg_sale_price_man": round(avg_sale_price_man, 0),
            "avg_sale_price_eon": round(avg_sale_price_man / 10000.0, 2),
            "avg_sale_pyeong_price": round(avg_sale_pp, 1),
            "median_sale_pyeong_price": round(median_sale_pp, 1),
            "est_market_90_pyeong_price": round(avg_sale_pp * 0.9, 1),
            "ref_est_sale_eon": round((avg_sale_pp * ref_pyeong * 0.9) / 10000.0, 2),
            "avg_rent_deposit_man": round(avg_rent_dep_man, 0),
            "avg_monthly_rent_man": round(avg_rent_monthly_man, 1),
            "avg_conv_deposit_man": round(avg_conv_dep_man, 0),
            "avg_conv_deposit_eon": round(avg_conv_dep_man / 10000.0, 2),
            "avg_conv_pyeong_price": round(avg_conv_pp, 1),
            "median_conv_pyeong_price": round(median_conv_pp, 1),
            "ref_est_conv_deposit_eon": round((avg_conv_pp * ref_pyeong) / 10000.0, 2),
            "jeonse_ratio_asking": round(naver_jeonse_ratio_asking, 1),
            "jeonse_ratio_est90": round(naver_jeonse_ratio_est90, 1),
            "age_group_summary": age_breakdown_summary,
            "group_comparisons": group_comparisons,
            "sale_items": naver_sale_items,
            "rent_items": naver_rent_items,
        },
        "realprice_analysis": {
            "primary": rp_primary,
            "selected_sale_pyeong_price": round(selected_rp_sale_pp, 1),
            "ref_realprice_sale_eon": round((selected_rp_sale_pp * ref_pyeong) / 10000.0, 2),
            "cross_jeonse_ratio_vs_naver_rent": cross_jeonse_ratio,
            "cross_jeonse_ratio_median": cross_jeonse_ratio_median,
            "sangga_jiphap": rp_sangga_jiphap,
            "sangga_ilban": rp_sangga_ilban,
            "officetel_rental_benchmark": rp_officetel_bench,
            "commercial_rent_note": (
                "국토부 실거래가 공개시스템은 법령상 상업·업무용(상가) 전월세 실거래를 비공개하므로, "
                "상가 실거래 매매 평당가 대비 네이버 실매물 환산보증금 교차 전세가율 및 동 상업지역 오피스텔 실거래 전세가율을 함께 산출했습니다."
                if ("상가" in ptype or "근린" in ptype)
                else ""
            ),
        },
    }
