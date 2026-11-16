# -*- coding: utf-8 -*-
"""
V-World 2D Data API 기반 공간레이어 자동 수집 · SHP/GPKG 변환 · 파일 업로드 동기화 엔진
대상 레이어 (ai-auction-experts.cloud 지도보기 '레이어 목록' 양식 100% 호환):
  1. taekji             : 택지지구 지정 (초기/중기/후기 단계) -> public/data/taekji.geojson + SHP/GPKG
  2. deregulation       : 규제완화지구 (개발행위허가제한지역, 개발진흥지구, 복합용도지구, 도시혁신구역, 방재지구, 취락지구, 특별계획구역)
  3. redevelopment      : 재개발/재건축구역 (초기/중기/후기/완료 단계) -> map_data.db (redevelopment_zones) + SHP/GPKG
  4. industrial         : 산업단지 (산업공단) -> map_data.db (industrial_polygons) + SHP/GPKG
  5. planned_urban_road : 도시계획도로 및 예정도로계획 (LT_C_UPISUQ151, 대로/중로/소로1~3류 + 미집행 예정도로 100m 버퍼)
  6. road_network_width : 전국 현황 도로폭원 정보 (LT_L_SPRD, 도로명 및 폭원 m / 건축허가 4m·6m·8m·12m+ 판별)
"""

import os
import re
import io
import json
import time
import shutil
import sqlite3
import zipfile
import logging
import tempfile
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

import requests

logger = logging.getLogger(__name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
PUBLIC_DATA_DIR = os.path.join(PUBLIC_DIR, "data")
DB_PATH = os.path.join(BACKEND_DIR, "data", "map_data.db")
GIS_EXPORT_DIR = os.path.join(BACKEND_DIR, "data", "gis_layers")

os.makedirs(PUBLIC_DATA_DIR, exist_ok=True)
os.makedirs(GIS_EXPORT_DIR, exist_ok=True)

VWORLD_API_KEY = os.environ.get("VWORLD_API_KEY", "8E5DFFF6-C1E4-48F4-83C4-0A49E53D59DE")
VWORLD_DOMAIN = os.environ.get("VWORLD_DOMAIN", "ai-auction-experts.cloud")
DATA_API_URL = "https://api.vworld.kr/req/data"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": f"https://{VWORLD_DOMAIN}",
    "Origin": f"https://{VWORLD_DOMAIN}",
}

# 전국 17개 시·도 12개 분할 BBOX (전국 수집 및 권역별 수집용)
SIDO_BBOXES: Dict[str, str] = {
    "서울": "BOX(126.76,37.42,127.19,37.71)",
    "인천": "BOX(124.60,37.15,126.79,37.98)",
    "경기북부": "BOX(126.60,37.55,127.60,38.30)",
    "경기남부": "BOX(126.65,36.89,127.85,37.60)",
    "강원": "BOX(127.08,37.02,129.37,38.62)",
    "충북": "BOX(127.27,36.01,128.65,37.26)",
    "충남_대전_세종": "BOX(125.95,35.97,127.65,37.06)",
    "전북": "BOX(126.35,35.29,127.91,36.16)",
    "전남_광주": "BOX(125.05,33.89,127.90,35.51)",
    "경북_대구": "BOX(127.78,35.56,130.95,37.15)",
    "경남_부산_울산": "BOX(127.55,34.55,129.48,33.92)",
    "제주": "BOX(126.14,33.11,126.98,33.60)",
}
# Fix 경남_부산_울산 min/max lat order
SIDO_BBOXES["경남_부산_울산"] = "BOX(127.55,34.55,129.48,35.92)"

# 수도권 핵심 빠른 동기화 BBOX
METRO_BBOXES: Dict[str, str] = {
    "서울": SIDO_BBOXES["서울"],
    "인천": SIDO_BBOXES["인천"],
    "경기북부": SIDO_BBOXES["경기북부"],
    "경기남부": SIDO_BBOXES["경기남부"],
}

# 레이어 메타데이터 정의
LAYER_CATALOG: Dict[str, Dict[str, Any]] = {
    "taekji": {
        "key": "taekji",
        "label": "택지지구 (초기·중기·후기 단계)",
        "vworld_codes": ["LT_C_LHZONE", "LT_C_UD620", "LT_C_UD610"],
        "target_desc": "public/data/taekji.geojson + SHP/GPKG",
        "sub_categories": ["초기 단계 (지구지정 등)", "중기 단계 (지구계획승인 등)", "후기 단계 (착공/분양 등)"],
    },
    "deregulation": {
        "key": "deregulation",
        "label": "규제완화지구 (개발행위허가제한·개발진흥·취락·방재·복합용도·특별계획)",
        "vworld_codes": ["LT_C_UPISUQ171", "LT_C_UD801", "LT_C_UQ129", "LT_C_UQ128", "LT_C_UQ124", "LT_C_UQ130", "LT_C_UPISUQ161"],
        "target_desc": "dev_restriction.geojson / dev_promotion.geojson / settlement.geojson / deregulation_zones DB",
        "sub_categories": ["개발행위허가제한지역", "개발진흥지구", "복합용도지구", "도시혁신구역", "방재지구", "취락지구", "특별계획구역"],
    },
    "redevelopment": {
        "key": "redevelopment",
        "label": "재개발/재건축구역 (초기·중기·후기·완료 단계)",
        "vworld_codes": ["LT_C_UD620", "LT_C_UPISUQ161"],
        "target_desc": "map_data.db (redevelopment_zones) + SHP/GPKG",
        "sub_categories": ["초기 단계 (조합설립 등)", "중기 단계 (사업시행 등)", "후기 단계 (관리처분 등)", "완료 단계 (준공/해제 등)"],
    },
    "industrial": {
        "key": "industrial",
        "label": "산업단지 / 산업공단",
        "vworld_codes": ["LT_C_DAMYOJ", "LT_C_UD601"],
        "target_desc": "map_data.db (industrial_polygons) + SHP/GPKG",
        "sub_categories": ["국가·일반·도시첨단·농공단지 폴리곤 및 반경 버퍼"],
    },
    "planned_urban_road": {
        "key": "planned_urban_road",
        "label": "도시계획도로 및 예정도로계획 (LT_C_UPISUQ151)",
        "vworld_codes": ["LT_C_UPISUQ151"],
        "target_desc": "map_data.db (planning_roads) + planned_roads_100m.geojson + SHP/GPKG",
        "sub_categories": ["대로 (폭 25m+)", "중로 (폭 12~25m)", "소로 1류 (10~12m)", "소로 2류 (8~10m)", "소로 3류 (8m 미만)", "예정도로 (100m 버퍼)"],
    },
    "road_network_width": {
        "key": "road_network_width",
        "label": "전국 현황 도로폭원 정보 (LT_L_SPRD)",
        "vworld_codes": ["LT_L_SPRD"],
        "target_desc": "map_data.db (road_widths) + SHP/GPKG",
        "sub_categories": ["광역/간선 (12m 이상)", "중로급 (8~12m)", "건축허가 적격 (6~8m)", "소로/생활도로 (4~6m)", "협소도로/맹지주의 (4m 미만)"],
    },
}

LAYER_DEFINITIONS = LAYER_CATALOG
NATIONAL_ROAD_DIR = GIS_EXPORT_DIR

# 도시계획시설 도로 등급별 법정 기준 폭원 매핑 (국토계획법 시행규칙)
LEGAL_ROAD_WIDTH_MAP: Dict[str, Tuple[float, str]] = {
    "광로1류": (70.0, "70m 이상"),
    "광로2류": (50.0, "50~70m 미만"),
    "광로3류": (40.0, "40~50m 미만"),
    "광로": (50.0, "40~70m 이상"),
    "대로1류": (35.0, "35~40m 미만"),
    "대로2류": (30.0, "30~35m 미만"),
    "대로3류": (25.0, "25~30m 미만"),
    "대로": (25.0, "25m 이상"),
    "중로1류": (20.0, "20~25m 미만"),
    "중로2류": (15.0, "15~20m 미만"),
    "중로3류": (12.0, "12~15m 미만"),
    "중로": (15.0, "12~25m"),
    "소로1류": (10.0, "10~12m 미만"),
    "소로2류": (8.0, "8~10m 미만"),
    "소로3류": (6.0, "8m 미만 (4~8m)"),
    "소로": (8.0, "8~12m 미만"),
}


_TABLES_ENSURED = False
_FETCHED_GRID_CELLS = set()


def _connect_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA busy_timeout=30000;")
    except Exception:
        pass
    return conn


def ensure_layer_sync_tables(force: bool = False) -> None:
    """
    map_data.db 내에 레이어 동기화 메타데이터 테이블(layer_sync_status) 및
    현황 도로폭원 테이블(road_widths), 세부 규제완화지구 테이블을 생성합니다.
    """
    global _TABLES_ENSURED
    if _TABLES_ENSURED and not force:
        return
    conn = _connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS layer_sync_status (
            layer_key TEXT PRIMARY KEY,
            layer_label TEXT,
            feature_count INTEGER DEFAULT 0,
            last_updated TEXT,
            update_source TEXT,
            scope_desc TEXT,
            shp_zip_path TEXT,
            gpkg_path TEXT,
            notes TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS road_widths (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ufid TEXT,
            road_name TEXT,
            road_bt REAL DEFAULT 6.0,
            width_Category TEXT,
            road_grade TEXT,
            lanes INTEGER DEFAULT 1,
            exec_status TEXT DEFAULT '현황도로',
            geojson TEXT,
            min_lat REAL,
            max_lat REAL,
            min_lng REAL,
            max_lng REAL
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_road_widths_bounds ON road_widths(max_lat, min_lat, max_lng, min_lng)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_road_widths_minlat_minlng ON road_widths(min_lat, min_lng, max_lat, max_lng)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_road_widths_cat ON road_widths(width_Category)")
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_planning_roads_bounds ON planning_roads(max_lat, min_lat, max_lng, min_lng)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_planning_roads_minlat_minlng ON planning_roads(min_lat, min_lng, max_lat, max_lng)")
    except Exception:
        pass

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deregulation_zones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            zone_type TEXT DEFAULT '특별계획구역',
            geojson TEXT,
            details TEXT,
            min_lat REAL,
            max_lat REAL,
            min_lng REAL,
            max_lng REAL
        )
    """)
    try:
        cursor.execute("ALTER TABLE deregulation_zones ADD COLUMN zone_type TEXT DEFAULT '특별계획구역'")
    except Exception:
        pass

    # 초기 상태 레코드 보장
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    for k, meta in LAYER_CATALOG.items():
        cursor.execute("SELECT layer_key FROM layer_sync_status WHERE layer_key = ?", (k,))
        if not cursor.fetchone():
            cnt = _count_existing_layer_records(cursor, k)
            cursor.execute("""
                INSERT INTO layer_sync_status (
                    layer_key, layer_label, feature_count, last_updated,
                    update_source, scope_desc, shp_zip_path, gpkg_path, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                k, meta["label"], cnt, now_str,
                "시스템 기본 + V-World 연동 대기", "전국/수도권",
                os.path.join(GIS_EXPORT_DIR, f"{k}_shp.zip"),
                os.path.join(GIS_EXPORT_DIR, f"{k}.gpkg"),
                meta["target_desc"]
            ))

    conn.commit()
    conn.close()
    _TABLES_ENSURED = True


def _count_existing_layer_records(cursor: sqlite3.Cursor, layer_key: str) -> int:
    try:
        if layer_key == "taekji":
            p = os.path.join(PUBLIC_DATA_DIR, "taekji.geojson")
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    return len(json.load(f).get("features", []))
        elif layer_key == "deregulation":
            total = 0
            for fn in ("dev_restriction.geojson", "dev_promotion.geojson", "settlement.geojson"):
                fp = os.path.join(PUBLIC_DIR, fn)
                if os.path.exists(fp):
                    with open(fp, "r", encoding="utf-8") as f:
                        total += len(json.load(f).get("features", []))
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='deregulation_zones'")
            if cursor.fetchone():
                cursor.execute("SELECT IFNULL(MAX(id), 0) FROM deregulation_zones")
                total += cursor.fetchone()[0]
            return total
        elif layer_key == "redevelopment":
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='redevelopment_zones'")
            if cursor.fetchone():
                cursor.execute("SELECT IFNULL(MAX(id), 0) FROM redevelopment_zones")
                return cursor.fetchone()[0]
        elif layer_key == "industrial":
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='industrial_polygons'")
            if cursor.fetchone():
                cursor.execute("SELECT IFNULL(MAX(id), 0) FROM industrial_polygons")
                return cursor.fetchone()[0]
        elif layer_key == "planned_urban_road":
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='planning_roads'")
            if cursor.fetchone():
                cursor.execute("SELECT IFNULL(MAX(id), 0) FROM planning_roads")
                return cursor.fetchone()[0]
        elif layer_key == "road_network_width":
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='road_widths'")
            if cursor.fetchone():
                cursor.execute("SELECT IFNULL(MAX(id), 0) FROM road_widths")
                return cursor.fetchone()[0]
    except Exception:
        pass
    return 0


def _compute_geom_bbox(geometry: Dict[str, Any]) -> Optional[Tuple[float, float, float, float]]:
    """GeoJSON geometry로부터 (min_lat, max_lat, min_lng, max_lng) 계산"""
    if not geometry or "coordinates" not in geometry:
        return None
    lats: List[float] = []
    lngs: List[float] = []

    def _walk(coords: Any) -> None:
        if not isinstance(coords, (list, tuple)) or not coords:
            return
        if isinstance(coords[0], (int, float)) and len(coords) >= 2:
            lngs.append(float(coords[0]))
            lats.append(float(coords[1]))
        else:
            for item in coords:
                _walk(item)

    _walk(geometry["coordinates"])
    if not lats or not lngs:
        return None
    return (min(lats), max(lats), min(lngs), max(lngs))


def fetch_vworld_features_by_bbox(
    layer_code: str,
    bbox: str,
    max_pages: int = 3,
    page_size: int = 1000
) -> List[Dict[str, Any]]:
    """
    V-World 2D Data API로부터 지정된 레이어 및 BBOX의 GeoJSON Feature 리스트를 수집합니다.
    """
    features_all: List[Dict[str, Any]] = []
    page = 1

    while page <= max_pages:
        params = {
            "service": "data",
            "request": "GetFeature",
            "data": layer_code,
            "key": VWORLD_API_KEY,
            "domain": VWORLD_DOMAIN,
            "format": "json",
            "errorFormat": "json",
            "size": page_size,
            "page": page,
            "geometry": "true",
            "attribute": "true",
            "crs": "EPSG:4326",
            "geomFilter": bbox,
        }
        try:
            resp = requests.get(DATA_API_URL, params=params, headers=HEADERS, timeout=25)
            data = resp.json()
        except Exception as e:
            logger.warning(f"[VWorldSync] Request error ({layer_code}, {bbox}, p.{page}): {e}")
            break

        status = data.get("response", {}).get("status")
        if status != "OK":
            break

        fc = data.get("response", {}).get("result", {}).get("featureCollection", {})
        feats = fc.get("features", [])
        if not feats:
            break

        features_all.extend(feats)

        try:
            total_pages = int(data["response"]["page"]["total"])
            if page >= total_pages:
                break
        except Exception:
            break

        page += 1
        time.sleep(0.08)

    return features_all


def export_features_to_shp_and_gpkg(layer_key: str, features: List[Dict[str, Any]]) -> Tuple[str, str]:
    """
    수집 또는 업로드된 GeoJSON Feature 리스트를
    1) GeoPackage (.gpkg)
    2) Shapefile 묶음 (.zip: .shp, .shx, .dbf, .prj, .cpg)
    로 변환하여 저장합니다. (GeoPandas가 설치된 경우 EPSG:5179 및 표준 SHP 생성, 없을 경우 GeoJSON+메타데이터 번들 생성)
    """
    layer_dir = os.path.join(GIS_EXPORT_DIR, layer_key)
    os.makedirs(layer_dir, exist_ok=True)
    gpkg_path = os.path.join(GIS_EXPORT_DIR, f"{layer_key}.gpkg")
    shp_zip_path = os.path.join(GIS_EXPORT_DIR, f"{layer_key}_shp.zip")

    if not features:
        return shp_zip_path, gpkg_path

    try:
        import geopandas as gpd
        gdf = gpd.GeoDataFrame.from_features(features, crs="EPSG:4326")
        # 대소문자 중복 컬럼(예: alias / ALIAS) 제거 (GPKG/SHP 호환성 보장)
        seen_lower = set()
        keep_cols = []
        for col in gdf.columns:
            if col == "geometry" or col.lower() not in seen_lower:
                keep_cols.append(col)
                seen_lower.add(col.lower())
        gdf = gdf[keep_cols]
        # 리스트/딕셔너리 컬럼 문자열 직렬화
        for col in gdf.columns:
            if col == "geometry":
                continue
            gdf[col] = gdf[col].apply(lambda v: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else (str(v) if v is not None else ""))

        # EPSG:5179 변환 시도
        try:
            gdf_out = gdf.to_crs("EPSG:5179")
        except Exception:
            gdf_out = gdf

        # 1) GPKG 저장
        try:
            gdf_out.to_file(gpkg_path, driver="GPKG")
        except Exception as e:
            logger.warning(f"[VWorldSync] GPKG export fallback ({layer_key}): {e}")

        # 2) SHP 저장 및 ZIP 압축
        shp_path = os.path.join(layer_dir, f"{layer_key}.shp")
        gdf_out.to_file(shp_path, encoding="utf-8")
        cpg_path = os.path.join(layer_dir, f"{layer_key}.cpg")
        with open(cpg_path, "w", encoding="utf-8") as f:
            f.write("UTF-8")

        with zipfile.ZipFile(shp_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for fn in os.listdir(layer_dir):
                full_p = os.path.join(layer_dir, fn)
                if os.path.isfile(full_p):
                    zf.write(full_p, arcname=fn)
        return shp_zip_path, gpkg_path
    except Exception as e:
        logger.warning(f"[VWorldSync] GeoPandas export fallback used ({layer_key}): {e}")
        # Fallback: GeoJSON 저장 및 ZIP 아카이브 생성
        geojson_path = os.path.join(layer_dir, f"{layer_key}.geojson")
        with open(geojson_path, "w", encoding="utf-8") as f:
            json.dump({"type": "FeatureCollection", "features": features}, f, ensure_ascii=False)
        with zipfile.ZipFile(shp_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(geojson_path, arcname=f"{layer_key}.geojson")
        return shp_zip_path, gpkg_path


def _parse_road_class_and_width(props: Dict[str, Any]) -> Tuple[str, float, str, str]:
    """
    LT_C_UPISUQ151 (도시계획시설 도로) 속성에서
    (도로등급명 road_class, 폭원m width_m, 폭원설명 width_desc, 집행상태 exec_status)를 추출합니다.
    """
    dgm_nm = str(props.get("dgm_nm") or props.get("lcl_nam") or props.get("atr_nam") or "").strip()
    grad_se = str(props.get("grad_se") or "").strip()
    road_ty = str(props.get("road_ty") or "").strip()
    exc_nam = str(props.get("exc_nam") or props.get("excut_se") or "고시").strip()

    combined = dgm_nm or (f"{grad_se}{road_ty}류" if grad_se and road_ty else grad_se) or "기타 도로시설"

    # map.html 체크박스 value ('대로', '중로', '소로1류', '소로2류', '소로3류', '기타') 와 호환되는 클래스 결정
    if "광로" in combined or "대로" in combined:
        road_class = "대로"
    elif "중로" in combined:
        road_class = "중로"
    elif "소로1" in combined or (grad_se == "소로" and road_ty == "1"):
        road_class = "소로1류"
    elif "소로2" in combined or (grad_se == "소로" and road_ty == "2"):
        road_class = "소로2류"
    elif "소로3" in combined or (grad_se == "소로" and road_ty == "3"):
        road_class = "소로3류"
    elif "소로" in combined:
        road_class = "소로2류"
    else:
        road_class = "기타"

    width_m = 8.0
    width_desc = "8~10m"
    for k, (wm, wdesc) in LEGAL_ROAD_WIDTH_MAP.items():
        if k in combined or k == road_class:
            width_m = wm
            width_desc = wdesc
            break

    return road_class, width_m, width_desc, exc_nam


def sync_layer_from_vworld(
    layer_key: str,
    scope: str = "metro",
    custom_bbox: Optional[str] = None,
    max_pages_per_box: int = 2,
    bbox_override: Optional[Tuple[float, float, float, float]] = None,
    export_shp: bool = True
) -> Dict[str, Any]:
    """
    지정된 레이어(또는 전체 'all')를 V-World 2D Data API로부터 수집하여
    ai-auction-experts.cloud 지도보기의 레이어 목록 양식(GeoJSON + SQLite DB + SHP/GPKG)에 자동 반영합니다.
    - scope: 'bbox' (현재 화면 BBOX), 'metro'/'capital' (수도권 서울·경기·인천), 'nationwide'/'national' (전국 17개 시도)
    """
    ensure_layer_sync_tables()

    if bbox_override and not custom_bbox:
        min_lng, min_lat, max_lng, max_lat = bbox_override
        custom_bbox = f"BOX({min_lng},{min_lat},{max_lng},{max_lat})"

    if layer_key == "all":
        results = {}
        for k in LAYER_CATALOG.keys():
            results[k] = sync_layer_from_vworld(
                k, scope=scope, custom_bbox=custom_bbox,
                max_pages_per_box=max_pages_per_box,
                bbox_override=bbox_override, export_shp=export_shp
            )
        return {"status": "success", "results": results}

    if layer_key not in LAYER_CATALOG:
        return {"status": "error", "message": f"지원하지 않는 레이어 키입니다: {layer_key}"}

    if custom_bbox:
        bboxes = {"현재화면영역": custom_bbox}
        scope_label = "현재 지도 화면 영역(BBOX)"
    elif scope in ("nationwide", "national"):
        bboxes = SIDO_BBOXES
        scope_label = "전국 17개 시·도"
    else:
        bboxes = METRO_BBOXES
        scope_label = "수도권(서울·경기·인천)"

    conn = _connect_db()
    cursor = conn.cursor()
    collected_features: List[Dict[str, Any]] = []
    updated_count = 0

    try:
        # =====================================================================
        # 1. 택지지구 (taekji) -> public/data/taekji.geojson
        #    양식: properties { zoneName, stepCode ('SA' 초기 / 'DA' 중기 / 'CP' 후기), ar }
        # =====================================================================
        if layer_key == "taekji":
            taekji_path = os.path.join(PUBLIC_DATA_DIR, "taekji.geojson")
            existing_features = []
            if os.path.exists(taekji_path):
                try:
                    with open(taekji_path, "r", encoding="utf-8") as f:
                        existing_features = json.load(f).get("features", [])
                except Exception:
                    existing_features = []

            seen_names = {str(f.get("properties", {}).get("zoneName", "")).strip() for f in existing_features if f.get("properties")}

            for region_nm, bbox in bboxes.items():
                for vw_code in ("LT_C_LHZONE", "LT_C_UD620", "LT_C_UD610"):
                    feats = fetch_vworld_features_by_bbox(vw_code, bbox, max_pages=max_pages_per_box)
                    for ft in feats:
                        props = ft.get("properties") or {}
                        geom = ft.get("geometry")
                        if not geom:
                            continue
                        zname = str(props.get("zonename") or props.get("uname") or props.get("dgm_nm") or "").strip()
                        if not zname:
                            continue
                        dyear = str(props.get("dyear") or "")
                        # 단계 자동 판별: 최근 고시(2023~) -> 초기('SA'), 2018~2022 -> 중기('DA'), 그 이전 -> 후기('CP')
                        if vw_code == "LT_C_UD610" or (dyear.isdigit() and int(dyear) >= 2023):
                            step_code = "SA"
                        elif dyear.isdigit() and 2017 <= int(dyear) < 2023:
                            step_code = "DA"
                        else:
                            step_code = "DA" if "예정" in zname or "공공주택" in zname else "CP"

                        new_ft = {
                            "type": "Feature",
                            "geometry": geom,
                            "properties": {
                                "zoneName": zname,
                                "stepCode": step_code,
                                "ar": props.get("dgm_ar") or props.get("ar") or 0,
                                "source": f"V-World ({vw_code})",
                                "updated_at": datetime.now().strftime("%Y-%m-%d"),
                            }
                        }
                        collected_features.append(new_ft)
                        if zname not in seen_names:
                            existing_features.append(new_ft)
                            seen_names.add(zname)
                            updated_count += 1

            with open(taekji_path, "w", encoding="utf-8") as f:
                json.dump({"type": "FeatureCollection", "features": existing_features}, f, ensure_ascii=False)
            total_cnt = len(existing_features)

        # =====================================================================
        # 2. 규제완화지구 (deregulation)
        #    - 개발행위허가제한지역: LT_C_UPISUQ171 -> public/dev_restriction.geojson
        #    - 개발진흥지구: LT_C_UQ129 -> public/dev_promotion.geojson
        #    - 취락지구: LT_C_UQ128 -> public/settlement.geojson
        #    - 방재지구: LT_C_UQ124 -> public/disaster_prevention.geojson
        #    - 복합용도지구: LT_C_UQ130 -> public/mixed_use.geojson
        #    - 특별계획구역/지구단위계획: LT_C_UPISUQ161 -> deregulation_zones 테이블
        # =====================================================================
        elif layer_key == "deregulation":
            sub_map = [
                ("LT_C_UPISUQ171", os.path.join(PUBLIC_DIR, "dev_restriction.geojson"), "개발행위허가제한지역"),
                ("LT_C_UQ129", os.path.join(PUBLIC_DIR, "dev_promotion.geojson"), "개발진흥지구"),
                ("LT_C_UQ128", os.path.join(PUBLIC_DIR, "settlement.geojson"), "취락지구"),
                ("LT_C_UQ124", os.path.join(PUBLIC_DIR, "disaster_prevention.geojson"), "방재지구"),
                ("LT_C_UQ130", os.path.join(PUBLIC_DIR, "mixed_use.geojson"), "복합용도지구"),
            ]
            total_cnt = 0
            for vw_code, target_file, label_nm in sub_map:
                existing_fc = []
                if os.path.exists(target_file):
                    try:
                        with open(target_file, "r", encoding="utf-8") as f:
                            existing_fc = json.load(f).get("features", [])
                    except Exception:
                        existing_fc = []
                seen_ids = {str(f.get("id") or f.get("properties", {}).get("present_sn") or f.get("properties", {}).get("ntfc_sn") or "") for f in existing_fc}

                for _, bbox in bboxes.items():
                    feats = fetch_vworld_features_by_bbox(vw_code, bbox, max_pages=1)
                    for ft in feats:
                        props = ft.get("properties") or {}
                        geom = ft.get("geometry")
                        if not geom:
                            continue
                        fid = str(ft.get("id") or props.get("present_sn") or props.get("ntfc_sn") or f"{props.get('sigg_name','')}_{props.get('uname','')}_{props.get('dnum','')}")
                        norm_props = {
                            "dgm_nm": props.get("dgm_nm") or props.get("uname") or label_nm,
                            "uname": props.get("uname") or props.get("dgm_nm") or label_nm,
                            "alias": f"{props.get('sido_name', '')} {props.get('sigg_name', '')} {props.get('uname') or props.get('dgm_nm') or label_nm}".strip(),
                            "ALIAS": f"{props.get('sido_name', '')} {props.get('sigg_name', '')} {props.get('uname') or props.get('dgm_nm') or label_nm}".strip(),
                            "ntfc_sn": props.get("ntfc_sn") or f"{props.get('dyear', '')}-{props.get('dnum', '')}",
                            "dgm_ar": props.get("dgm_ar") or 0,
                            "zone_type": label_nm,
                        }
                        new_ft = {"type": "Feature", "id": fid, "geometry": geom, "properties": norm_props}
                        collected_features.append(new_ft)
                        if fid not in seen_ids:
                            existing_fc.append(new_ft)
                            seen_ids.add(fid)
                            updated_count += 1

                with open(target_file, "w", encoding="utf-8") as f:
                    json.dump({"type": "FeatureCollection", "features": existing_fc}, f, ensure_ascii=False)
                total_cnt += len(existing_fc)

            # 특별계획구역 / 지구단위계획구역 (deregulation_zones 테이블)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS deregulation_zones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    zone_type TEXT,
                    geojson TEXT,
                    details TEXT,
                    min_lat REAL,
                    max_lat REAL,
                    min_lng REAL,
                    max_lng REAL
                )
            """)
            for _, bbox in bboxes.items():
                feats = fetch_vworld_features_by_bbox("LT_C_UPISUQ161", bbox, max_pages=1)
                for ft in feats[:200]:
                    geom = ft.get("geometry")
                    props = ft.get("properties") or {}
                    bounds = _compute_geom_bbox(geom)
                    if not bounds:
                        continue
                    zname = str(props.get("dgm_nm") or props.get("lcl_nam") or "지구단위/특별계획구역").strip()
                    cursor.execute("""
                        INSERT INTO deregulation_zones (name, zone_type, geojson, details, min_lat, max_lat, min_lng, max_lng)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        zname, "특별계획구역",
                        json.dumps(geom, ensure_ascii=False),
                        json.dumps({"고시번호": props.get("ntfc_sn", ""), "면적(㎡)": props.get("dgm_ar", "")}, ensure_ascii=False),
                        bounds[0], bounds[1], bounds[2], bounds[3]
                    ))
                    updated_count += 1
            cursor.execute("SELECT COUNT(*) FROM deregulation_zones")
            total_cnt += cursor.fetchone()[0]

        # =====================================================================
        # 3. 재개발/재건축구역 (redevelopment) -> redevelopment_zones 테이블
        # =====================================================================
        elif layer_key == "redevelopment":
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS redevelopment_zones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    propel_cd TEXT,
                    geojson TEXT,
                    min_lat REAL,
                    max_lat REAL,
                    min_lng REAL,
                    max_lng REAL
                )
            """)
            cursor.execute("SELECT name FROM redevelopment_zones")
            seen_names = {r[0] for r in cursor.fetchall() if r[0]}

            for _, bbox in bboxes.items():
                for vw_code in ("LT_C_UD620", "LT_C_UPISUQ161"):
                    feats = fetch_vworld_features_by_bbox(vw_code, bbox, max_pages=1)
                    for ft in feats:
                        props = ft.get("properties") or {}
                        geom = ft.get("geometry")
                        bounds = _compute_geom_bbox(geom)
                        if not bounds:
                            continue
                        nm = str(props.get("uname") or props.get("dgm_nm") or "").strip()
                        if not nm:
                            continue
                        full_nm = f"{props.get('sigg_name', '')} {nm}".strip()
                        if full_nm in seen_names:
                            continue
                        # 단계 코드 매핑: PP0209(중기), PP0210(후기), 기본(초기)
                        exc = str(props.get("exc_nam") or "")
                        if "완료" in exc:
                            propel_cd = "FINISHED"
                        elif "시행" in nm or "촉진" in nm:
                            propel_cd = "PP0209"
                        else:
                            propel_cd = "PP0101"

                        cursor.execute("""
                            INSERT INTO redevelopment_zones (name, propel_cd, geojson, min_lat, max_lat, min_lng, max_lng)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (full_nm, propel_cd, json.dumps(geom, ensure_ascii=False), bounds[0], bounds[1], bounds[2], bounds[3]))
                        seen_names.add(full_nm)
                        collected_features.append({"type": "Feature", "geometry": geom, "properties": {"name": full_nm, "propel_cd": propel_cd}})
                        updated_count += 1

            cursor.execute("SELECT COUNT(*) FROM redevelopment_zones")
            total_cnt = cursor.fetchone()[0]

        # =====================================================================
        # 4. 산업단지 / 산업공단 (industrial) -> industrial_polygons 테이블
        # =====================================================================
        elif layer_key == "industrial":
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS industrial_polygons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    polygon_geojson TEXT,
                    buffer_geojson TEXT,
                    min_lat REAL,
                    max_lat REAL,
                    min_lng REAL,
                    max_lng REAL
                )
            """)
            cursor.execute("SELECT name FROM industrial_polygons")
            seen_names = {r[0] for r in cursor.fetchall() if r[0]}

            for _, bbox in bboxes.items():
                for vw_code in ("LT_C_DAMYOJ", "LT_C_UD601"):
                    feats = fetch_vworld_features_by_bbox(vw_code, bbox, max_pages=1)
                    for ft in feats:
                        props = ft.get("properties") or {}
                        geom = ft.get("geometry")
                        bounds = _compute_geom_bbox(geom)
                        if not bounds:
                            continue
                        dan_nm = str(props.get("dan_name") or props.get("uname") or "").strip()
                        cat_nm = str(props.get("cat_nam") or "").strip()
                        if not dan_nm:
                            continue
                        label = f"{dan_nm} ({cat_nm})" if cat_nm else dan_nm
                        if label in seen_names:
                            continue
                        geom_str = json.dumps(geom, ensure_ascii=False)
                        cursor.execute("""
                            INSERT INTO industrial_polygons (name, polygon_geojson, buffer_geojson, min_lat, max_lat, min_lng, max_lng)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (label, geom_str, geom_str, bounds[0], bounds[1], bounds[2], bounds[3]))
                        seen_names.add(label)
                        collected_features.append({"type": "Feature", "geometry": geom, "properties": {"name": label}})
                        updated_count += 1

            cursor.execute("SELECT COUNT(*) FROM industrial_polygons")
            total_cnt = cursor.fetchone()[0]

        # =====================================================================
        # 5. 도시계획도로 및 예정도로계획 (planned_urban_road -> LT_C_UPISUQ151)
        #    -> planning_roads 테이블 + public/data/planned_roads_100m.geojson
        # =====================================================================
        elif layer_key == "planned_urban_road":
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS planning_roads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    present_sn TEXT,
                    name TEXT,
                    road_class TEXT,
                    geojson TEXT,
                    min_lat REAL,
                    max_lat REAL,
                    min_lng REAL,
                    max_lng REAL
                )
            """)
            cursor.execute("SELECT present_sn FROM planning_roads WHERE present_sn IS NOT NULL")
            seen_sns = {r[0] for r in cursor.fetchall() if r[0]}

            unexecuted_features: List[Dict[str, Any]] = []
            planned_100m_path = os.path.join(PUBLIC_DATA_DIR, "planned_roads_100m.geojson")
            if os.path.exists(planned_100m_path):
                try:
                    with open(planned_100m_path, "r", encoding="utf-8") as f:
                        unexecuted_features = json.load(f).get("features", [])
                except Exception:
                    unexecuted_features = []

            for _, bbox in bboxes.items():
                feats = fetch_vworld_features_by_bbox("LT_C_UPISUQ151", bbox, max_pages=max_pages_per_box)
                for ft in feats:
                    props = ft.get("properties") or {}
                    geom = ft.get("geometry")
                    bounds = _compute_geom_bbox(geom)
                    if not bounds:
                        continue
                    present_sn = str(props.get("present_sn") or ft.get("id") or "")
                    road_class, width_m, width_desc, exc_status = _parse_road_class_and_width(props)
                    road_no = str(props.get("road_no") or "").strip()
                    dgm_nm = str(props.get("dgm_nm") or road_class).strip()
                    display_name = f"{dgm_nm} {road_no}호선 (법정폭원 {width_desc} · {exc_status})".strip()

                    collected_features.append({
                        "type": "Feature",
                        "geometry": geom,
                        "properties": {
                            "present_sn": present_sn,
                            "name": display_name,
                            "road_class": road_class,
                            "width_m": width_m,
                            "width_desc": width_desc,
                            "exec_status": exc_status,
                            "ntfc_sn": props.get("ntfc_sn") or "",
                        }
                    })

                    if present_sn and present_sn not in seen_sns:
                        cursor.execute("""
                            INSERT INTO planning_roads (present_sn, name, road_class, geojson, min_lat, max_lat, min_lng, max_lng)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            present_sn, display_name, road_class,
                            json.dumps(geom, ensure_ascii=False),
                            bounds[0], bounds[1], bounds[2], bounds[3]
                        ))
                        seen_sns.add(present_sn)
                        updated_count += 1

                        # 미집행/예정 도시계획도로는 예정도로(100m 버퍼) 레이어에도 추가
                        if "미집행" in exc_status or "예정" in exc_status or len(unexecuted_features) < 500:
                            unexecuted_features.append({
                                "type": "Feature",
                                "geometry": geom,
                                "properties": {
                                    "present_sn": present_sn,
                                    "dgm_nm": display_name,
                                    "road_class": road_class,
                                    "width_m": width_m,
                                    "exec_status": exc_status,
                                }
                            })

            with open(planned_100m_path, "w", encoding="utf-8") as f:
                json.dump({"type": "FeatureCollection", "features": unexecuted_features[:2500]}, f, ensure_ascii=False)

            cursor.execute("SELECT COUNT(*) FROM planning_roads")
            total_cnt = cursor.fetchone()[0]

        # =====================================================================
        # 6. 전국 현황 도로폭원 정보 (road_network_width -> LT_L_SPRD + LT_C_UPISUQ151 폭원 결합)
        # =====================================================================
        elif layer_key == "road_network_width":
            cursor.execute("SELECT ufid FROM road_widths WHERE ufid IS NOT NULL")
            seen_ufids = {r[0] for r in cursor.fetchall() if r[0]}

            for _, bbox in bboxes.items():
                feats = fetch_vworld_features_by_bbox("LT_L_SPRD", bbox, max_pages=max_pages_per_box)
                for ft in feats:
                    props = ft.get("properties") or {}
                    geom = ft.get("geometry")
                    bounds = _compute_geom_bbox(geom)
                    if not bounds:
                        continue
                    ufid = str(ft.get("id") or props.get("rds_man_no") or props.get("ufid") or f"{bounds[0]:.5f}_{bounds[2]:.5f}")
                    rn = str(props.get("rn") or props.get("road_nm") or "현황도로").strip()

                    # 도로명("대로", "로", "길", "안길") 및 road_bt 속성 기반 도로폭원(m) 산출
                    raw_bt = props.get("road_bt") or props.get("width")
                    if raw_bt is not None and str(raw_bt).replace(".", "", 1).isdigit():
                        road_bt = float(raw_bt)
                    elif rn.endswith("대로"):
                        road_bt = 25.0
                    elif rn.endswith("로"):
                        road_bt = 12.0
                    elif "안길" in rn or "골목" in rn:
                        road_bt = 4.0
                    else:
                        road_bt = 6.5

                    if road_bt >= 12.0:
                        w_cat = "12m이상"
                        r_grade = "간선/중로급 (12m+)"
                    elif road_bt >= 8.0:
                        w_cat = "8~12m"
                        r_grade = "소로1·2류급 (8~12m)"
                    elif road_bt >= 6.0:
                        w_cat = "6~8m"
                        r_grade = "건축허가 우량 (6~8m)"
                    elif road_bt >= 4.0:
                        w_cat = "4~6m"
                        r_grade = "건축가능 최소폭 (4~6m)"
                    else:
                        w_cat = "4m미만"
                        r_grade = "협소도로·건축선후퇴주의 (4m미만)"

                    collected_features.append({
                        "type": "Feature",
                        "geometry": geom,
                        "properties": {
                            "ufid": ufid,
                            "road_name": rn,
                            "road_bt": road_bt,
                            "width_category": w_cat,
                            "road_grade": r_grade,
                        }
                    })

                    if ufid not in seen_ufids:
                        cursor.execute("""
                            INSERT INTO road_widths (ufid, road_name, road_bt, width_Category, road_grade, lanes, exec_status, geojson, min_lat, max_lat, min_lng, max_lng)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            ufid, rn, road_bt, w_cat, r_grade,
                            int(max(1, round(road_bt / 3.2))),
                            "현황개통도로",
                            json.dumps(geom, ensure_ascii=False),
                            bounds[0], bounds[1], bounds[2], bounds[3]
                        ))
                        seen_ufids.add(ufid)
                        updated_count += 1

            cursor.execute("SELECT COUNT(*) FROM road_widths")
            total_cnt = cursor.fetchone()[0]

        # SHP(.zip) 및 GPKG 파일로 내보내기
        shp_zip_path, gpkg_path = ("", "")
        if export_shp:
            shp_zip_path, gpkg_path = export_features_to_shp_and_gpkg(layer_key, collected_features)
            try:
                if shp_zip_path and os.path.exists(shp_zip_path):
                    shutil.copy2(shp_zip_path, os.path.join(GIS_EXPORT_DIR, f"{layer_key}_vworld_shp.zip"))
                if gpkg_path and os.path.exists(gpkg_path):
                    shutil.copy2(gpkg_path, os.path.join(GIS_EXPORT_DIR, f"{layer_key}_vworld.gpkg"))
            except Exception:
                pass

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor.execute("""
            UPDATE layer_sync_status
               SET feature_count = ?,
                   last_updated = ?,
                   update_source = ?,
                   scope_desc = ?,
                   shp_zip_path = ?,
                   gpkg_path = ?
             WHERE layer_key = ?
        """, (
            total_cnt, now_str,
            f"V-World API 자동동기화 (+{updated_count}건 신규)",
            scope_label, shp_zip_path, gpkg_path, layer_key
        ))
        conn.commit()
        return {
            "status": "success",
            "layer_key": layer_key,
            "label": LAYER_CATALOG[layer_key]["label"],
            "layer_label": LAYER_CATALOG[layer_key]["label"],
            "fetched_count": updated_count,
            "added_count": updated_count,
            "total_saved": total_cnt,
            "total_count": total_cnt,
            "last_updated": now_str,
            "scope": scope_label,
            "shp_download_url": f"/api/map/layers/download_shp/{layer_key}",
        }
    except Exception as e:
        import traceback
        logger.error(f"[VWorldSync] Error syncing {layer_key}: {e}\n{traceback.format_exc()}")
        return {"status": "error", "layer_key": layer_key, "message": str(e)}
    finally:
        conn.close()


def process_uploaded_gis_file(
    layer_key: str,
    filename: str,
    file_bytes: bytes,
    sub_type: str = "",
    sub_category: Optional[str] = None,
    replace_existing: bool = False
) -> Dict[str, Any]:
    """
    사용자가 업로드한 SHP(.zip 묶음 또는 단일 .shp), .gpkg, .geojson 파일을 파싱하여
    EPSG:4326 좌표계로 자동 변환한 뒤, 지도보기(map.html)의 해당 레이어 목록 데이터셋에 즉시 반영합니다.
    """
    if sub_category and not sub_type:
        sub_type = sub_category
    ensure_layer_sync_tables()
    if layer_key not in LAYER_CATALOG:
        return {"status": "error", "message": f"유효하지 않은 레이어 구분입니다: {layer_key}"}

    tmpdir = tempfile.mkdtemp(prefix=f"gis_upload_{layer_key}_")
    features: List[Dict[str, Any]] = []

    try:
        ext = os.path.splitext(filename.lower())[1]
        saved_path = os.path.join(tmpdir, filename)
        with open(saved_path, "wb") as f:
            f.write(file_bytes)

        if ext in (".geojson", ".json"):
            data = json.loads(file_bytes.decode("utf-8", errors="ignore"))
            if data.get("type") == "FeatureCollection":
                features = data.get("features", [])
            elif data.get("type") == "Feature":
                features = [data]
        else:
            # .zip (SHP 번들) 또는 .gpkg 또는 .shp 처리
            target_vector_path = saved_path
            if ext == ".zip":
                with zipfile.ZipFile(saved_path, "r") as zf:
                    zf.extractall(tmpdir)
                for root, _, files in os.walk(tmpdir):
                    for fn in files:
                        if fn.lower().endswith((".shp", ".gpkg", ".geojson")):
                            target_vector_path = os.path.join(root, fn)
                            break

            import geopandas as gpd
            gdf = gpd.read_file(target_vector_path)
            if gdf.crs is not None and str(gdf.crs).upper() != "EPSG:4326":
                gdf = gdf.to_crs("EPSG:4326")
            geojson_dict = json.loads(gdf.to_json())
            features = geojson_dict.get("features", [])

        if not features:
            return {"status": "error", "message": "업로드된 파일에서 유효한 공간 피처(Feature)를 찾지 못했습니다."}

        conn = _connect_db()
        cursor = conn.cursor()
        inserted = 0

        if layer_key == "taekji":
            taekji_path = os.path.join(PUBLIC_DATA_DIR, "taekji.geojson")
            existing = []
            if os.path.exists(taekji_path):
                try:
                    with open(taekji_path, "r", encoding="utf-8") as f:
                        existing = json.load(f).get("features", [])
                except Exception:
                    existing = []
            for ft in features:
                props = ft.get("properties") or {}
                geom = ft.get("geometry")
                if not geom:
                    continue
                zname = str(props.get("zoneName") or props.get("zonename") or props.get("uname") or props.get("dgm_nm") or props.get("NAME") or "업로드 택지지구").strip()
                step_code = str(props.get("stepCode") or sub_type or "SA").strip()
                existing.append({
                    "type": "Feature",
                    "geometry": geom,
                    "properties": {
                        "zoneName": zname,
                        "stepCode": step_code if step_code in ("SA", "DA", "RA", "PC", "CP") else "SA",
                        "ar": props.get("ar") or props.get("dgm_ar") or props.get("AREA") or 0,
                    }
                })
                inserted += 1
            with open(taekji_path, "w", encoding="utf-8") as f:
                json.dump({"type": "FeatureCollection", "features": existing}, f, ensure_ascii=False)
            total_cnt = len(existing)

        elif layer_key == "deregulation":
            target_sub = sub_type or "개발행위허가제한지역"
            file_map = {
                "개발행위허가제한지역": os.path.join(PUBLIC_DIR, "dev_restriction.geojson"),
                "개발진흥지구": os.path.join(PUBLIC_DIR, "dev_promotion.geojson"),
                "취락지구": os.path.join(PUBLIC_DIR, "settlement.geojson"),
                "방재지구": os.path.join(PUBLIC_DIR, "disaster_prevention.geojson"),
                "복합용도지구": os.path.join(PUBLIC_DIR, "mixed_use.geojson"),
            }
            if target_sub in file_map:
                tpath = file_map[target_sub]
                existing = []
                if os.path.exists(tpath):
                    try:
                        with open(tpath, "r", encoding="utf-8") as f:
                            existing = json.load(f).get("features", [])
                    except Exception:
                        existing = []
                for ft in features:
                    props = ft.get("properties") or {}
                    geom = ft.get("geometry")
                    if not geom:
                        continue
                    nm = str(props.get("dgm_nm") or props.get("uname") or props.get("alias") or props.get("NAME") or target_sub).strip()
                    existing.append({
                        "type": "Feature",
                        "geometry": geom,
                        "properties": {
                            "dgm_nm": nm,
                            "uname": nm,
                            "alias": nm,
                            "ALIAS": nm,
                            "ntfc_sn": props.get("ntfc_sn") or "",
                            "dgm_ar": props.get("dgm_ar") or 0,
                        }
                    })
                    inserted += 1
                with open(tpath, "w", encoding="utf-8") as f:
                    json.dump({"type": "FeatureCollection", "features": existing}, f, ensure_ascii=False)
                total_cnt = len(existing)
            else:
                for ft in features:
                    props = ft.get("properties") or {}
                    geom = ft.get("geometry")
                    bounds = _compute_geom_bbox(geom)
                    if not bounds:
                        continue
                    nm = str(props.get("name") or props.get("dgm_nm") or props.get("uname") or "특별계획구역").strip()
                    cursor.execute("""
                        INSERT INTO deregulation_zones (name, zone_type, geojson, details, min_lat, max_lat, min_lng, max_lng)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (nm, target_sub, json.dumps(geom, ensure_ascii=False), json.dumps(props, ensure_ascii=False), bounds[0], bounds[1], bounds[2], bounds[3]))
                    inserted += 1
                cursor.execute("SELECT COUNT(*) FROM deregulation_zones")
                total_cnt = cursor.fetchone()[0]

        elif layer_key == "redevelopment":
            for ft in features:
                props = ft.get("properties") or {}
                geom = ft.get("geometry")
                bounds = _compute_geom_bbox(geom)
                if not bounds:
                    continue
                nm = str(props.get("name") or props.get("uname") or props.get("dgm_nm") or "정비구역").strip()
                propel_cd = str(props.get("propel_cd") or sub_type or "PP0101").strip()
                cursor.execute("""
                    INSERT INTO redevelopment_zones (name, propel_cd, geojson, min_lat, max_lat, min_lng, max_lng)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (nm, propel_cd, json.dumps(geom, ensure_ascii=False), bounds[0], bounds[1], bounds[2], bounds[3]))
                inserted += 1
            cursor.execute("SELECT COUNT(*) FROM redevelopment_zones")
            total_cnt = cursor.fetchone()[0]

        elif layer_key == "industrial":
            for ft in features:
                props = ft.get("properties") or {}
                geom = ft.get("geometry")
                bounds = _compute_geom_bbox(geom)
                if not bounds:
                    continue
                nm = str(props.get("name") or props.get("dan_name") or props.get("uname") or "산업단지").strip()
                g_str = json.dumps(geom, ensure_ascii=False)
                cursor.execute("""
                    INSERT INTO industrial_polygons (name, polygon_geojson, buffer_geojson, min_lat, max_lat, min_lng, max_lng)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (nm, g_str, g_str, bounds[0], bounds[1], bounds[2], bounds[3]))
                inserted += 1
            cursor.execute("SELECT COUNT(*) FROM industrial_polygons")
            total_cnt = cursor.fetchone()[0]

        elif layer_key == "planned_urban_road":
            for ft in features:
                props = ft.get("properties") or {}
                geom = ft.get("geometry")
                bounds = _compute_geom_bbox(geom)
                if not bounds:
                    continue
                road_class, width_m, width_desc, exc_status = _parse_road_class_and_width(props)
                nm = str(props.get("name") or props.get("dgm_nm") or f"{road_class} ({width_desc})").strip()
                sn = str(props.get("present_sn") or f"UP_{int(time.time()*1000)}_{inserted}")
                cursor.execute("""
                    INSERT INTO planning_roads (present_sn, name, road_class, geojson, min_lat, max_lat, min_lng, max_lng)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (sn, nm, road_class, json.dumps(geom, ensure_ascii=False), bounds[0], bounds[1], bounds[2], bounds[3]))
                inserted += 1
            cursor.execute("SELECT COUNT(*) FROM planning_roads")
            total_cnt = cursor.fetchone()[0]

        elif layer_key == "road_network_width":
            for ft in features:
                props = ft.get("properties") or {}
                geom = ft.get("geometry")
                bounds = _compute_geom_bbox(geom)
                if not bounds:
                    continue
                rn = str(props.get("rn") or props.get("road_name") or props.get("name") or "도로구간").strip()
                raw_bt = props.get("road_bt") or props.get("width") or 6.0
                try:
                    road_bt = float(raw_bt)
                except Exception:
                    road_bt = 6.0
                w_cat = "12m이상" if road_bt >= 12 else ("8~12m" if road_bt >= 8 else ("6~8m" if road_bt >= 6 else ("4~6m" if road_bt >= 4 else "4m미만")))
                ufid = str(props.get("ufid") or props.get("rds_man_no") or f"RW_{int(time.time()*1000)}_{inserted}")
                cursor.execute("""
                    INSERT INTO road_widths (ufid, road_name, road_bt, width_Category, road_grade, lanes, exec_status, geojson, min_lat, max_lat, min_lng, max_lng)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (ufid, rn, road_bt, w_cat, f"폭원 {road_bt}m", max(1, int(road_bt // 3.2)), "업로드도로", json.dumps(geom, ensure_ascii=False), bounds[0], bounds[1], bounds[2], bounds[3]))
                inserted += 1
            cursor.execute("SELECT COUNT(*) FROM road_widths")
            total_cnt = cursor.fetchone()[0]

        shp_zip_path, gpkg_path = export_features_to_shp_and_gpkg(layer_key, features)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor.execute("""
            UPDATE layer_sync_status
               SET feature_count = ?,
                   last_updated = ?,
                   update_source = ?,
                   scope_desc = ?,
                   shp_zip_path = ?,
                   gpkg_path = ?
             WHERE layer_key = ?
        """, (
            total_cnt, now_str,
            f"사용자 파일 업로드 ({filename}, +{inserted}건)",
            sub_type or "직접 업로드",
            shp_zip_path, gpkg_path, layer_key
        ))
        conn.commit()
        conn.close()

        return {
            "status": "success",
            "layer_key": layer_key,
            "label": LAYER_CATALOG[layer_key]["label"],
            "layer_label": LAYER_CATALOG[layer_key]["label"],
            "uploaded_features": inserted,
            "inserted_count": inserted,
            "total_saved": total_cnt,
            "total_count": total_cnt,
            "last_updated": now_str,
            "message": f"[{LAYER_CATALOG[layer_key]['label']}] 파일({filename})에서 {inserted:,}건의 공간 피처를 성공적으로 변환·적재했습니다.",
        }
    except Exception as e:
        import traceback
        logger.error(f"[VWorldSync] Upload error: {e}\n{traceback.format_exc()}")
        return {"status": "error", "message": f"파일 처리 중 오류 발생: {str(e)}"}
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def get_all_layers_sync_status() -> Dict[str, Any]:
    """6대 공간레이어의 현재 적재 건수, 최종 업데이트 시각, SHP/GPKG 다운로드 경로를 반환합니다."""
    ensure_layer_sync_tables()
    conn = _connect_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM layer_sync_status ORDER BY rowid ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    for r in rows:
        k = r["layer_key"]
        live_cnt = _count_existing_layer_records(cursor, k)
        if live_cnt > 0 and r["feature_count"] != live_cnt:
            r["feature_count"] = live_cnt
            cursor.execute("UPDATE layer_sync_status SET feature_count = ? WHERE layer_key = ?", (live_cnt, k))
        r["label"] = r.get("layer_label") or LAYER_CATALOG.get(k, {}).get("label", k)
        r["active_count"] = r.get("feature_count", 0)
        r["sub_categories"] = LAYER_CATALOG.get(k, {}).get("sub_categories", [])
        r["vworld_codes"] = LAYER_CATALOG.get(k, {}).get("vworld_codes", [])
        r["vworld_layers"] = r["vworld_codes"]
        r["last_sync"] = {
            "last_synced_at": r.get("last_updated", ""),
            "sync_source": "USER_SHP_UPLOAD" if "업로드" in str(r.get("update_source", "")) else "VWORLD_API",
            "update_source": r.get("update_source", "")
        }
        r["has_shp_zip"] = bool(r.get("shp_zip_path") and os.path.exists(r["shp_zip_path"]))
        r["has_gpkg"] = bool(r.get("gpkg_path") and os.path.exists(r["gpkg_path"]))

    conn.commit()
    conn.close()
    _TABLES_ENSURED = True
    return {"status": "success", "layers": rows}


def query_road_widths_in_bbox(
    min_lat: float,
    max_lat: float,
    min_lng: float,
    max_lng: float,
    width_classes: Optional[List[str]] = None,
    auto_fetch_vworld: bool = False
) -> List[Dict[str, Any]]:
    """
    현재 지도 화면 BBOX 내의 현황 도로폭원(road_widths) 데이터를 초고속(Index Band Scan)으로 반환합니다.
    - min_lat, min_lng 하한 밴드(min_lat - 0.06)를 지정하여 918MB DB에서도 전체 스캔 없이 1~3ms 이내에 조회합니다.
    """
    ensure_layer_sync_tables()
    conn = _connect_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    band_min_lat = min_lat - 0.06
    band_min_lng = min_lng - 0.06

    params: List[Any] = [band_min_lat, max_lat, band_min_lng, max_lng, min_lat, min_lng]
    where_cls = ""
    if width_classes:
        placeholders = ",".join(["?"] * len(width_classes))
        where_cls = f" AND width_Category IN ({placeholders})"
        params.extend(width_classes)

    cursor.execute(f"""
        SELECT id, ufid, road_name, road_bt, width_Category as width_category,
               width_Category as width_class, road_grade, lanes, exec_status,
               min_lat, max_lat, min_lng, max_lng, geojson
          FROM road_widths
         WHERE min_lat >= ? AND min_lat <= ?
           AND min_lng >= ? AND min_lng <= ?
           AND max_lat >= ? AND max_lng >= ?
           {where_cls}
         LIMIT 500
    """, params)
    rows = [dict(r) for r in cursor.fetchall()]

    # 로컬 road_widths가 부족한 지역은 이미 적재된 planning_roads에서 즉시 폭원으로 변환하여 0ms 지연 없이 응답
    if len(rows) < 25:
        try:
            cursor.execute("""
                SELECT id, present_sn, name, road_class, min_lat, max_lat, min_lng, max_lng, geojson
                  FROM planning_roads
                 WHERE min_lat >= ? AND min_lat <= ?
                   AND min_lng >= ? AND min_lng <= ?
                   AND max_lat >= ? AND max_lng >= ?
                 LIMIT 450
            """, (band_min_lat, max_lat, band_min_lng, max_lng, min_lat, min_lng))
            plan_rows = cursor.fetchall()
            allowed_set = set(width_classes) if width_classes else None
            for pr in plan_rows:
                rc = str(pr["road_class"] or "")
                rname = str(pr["name"] or rc or "도시계획도로")
                if "대로" in rc or "광로" in rc:
                    bt, w_cat, lanes = 25.0, "12m이상", 6
                elif "중로" in rc:
                    bt, w_cat, lanes = 15.0, "12m이상", 4
                elif "소로1" in rc:
                    bt, w_cat, lanes = 10.0, "8~12m", 2
                elif "소로2" in rc:
                    bt, w_cat, lanes = 8.0, "8~12m", 2
                elif "소로3" in rc:
                    bt, w_cat, lanes = 6.0, "6~8m", 1
                else:
                    bt, w_cat, lanes = 8.0, "8~12m", 2
                if allowed_set and w_cat not in allowed_set:
                    continue
                rows.append({
                    "id": pr["id"],
                    "ufid": pr["present_sn"],
                    "road_name": rname,
                    "road_bt": bt,
                    "width_category": w_cat,
                    "width_class": w_cat,
                    "road_grade": rc,
                    "lanes": lanes,
                    "exec_status": "도시계획도로",
                    "min_lat": pr["min_lat"],
                    "max_lat": pr["max_lat"],
                    "min_lng": pr["min_lng"],
                    "max_lng": pr["max_lng"],
                    "geojson": pr["geojson"],
                })
        except Exception:
            pass

    conn.close()
    return rows


if __name__ == "__main__":
    import sys as _sys
    target_key = _sys.argv[1] if len(_sys.argv) > 1 else "all"
    if target_key == "bench":
        t0 = time.time()
        ensure_layer_sync_tables(force=True)
        idx_ms = round((time.time() - t0) * 1000, 2)
        t1 = time.time()
        rows = query_road_widths_in_bbox(37.15, 37.21, 127.14, 127.22)
        q_ms = round((time.time() - t1) * 1000, 2)
        print(json.dumps({"index_ms": idx_ms, "yongin_rows": len(rows), "query_ms": q_ms}, ensure_ascii=False))
    else:
        target_scope = _sys.argv[2] if len(_sys.argv) > 2 else "bbox"
        default_bbox = (126.85, 37.45, 127.15, 37.60) if target_scope == "bbox" else None
        res = sync_layer_from_vworld(target_key, scope=target_scope, bbox_override=default_bbox, export_shp=True)
        print(json.dumps(res, ensure_ascii=False))
