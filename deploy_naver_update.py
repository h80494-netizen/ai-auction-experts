import os
import sys
import io
import gzip
import json
import time
import shutil
import sqlite3
import tempfile
import subprocess
import urllib.request
import urllib.parse
from dotenv import load_dotenv

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', write_through=True)
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

LOCAL_DB_PATH = os.path.join(BASE_DIR, 'backend', 'data', 'map_data.db')
AWS_HOST = os.getenv('AWS_HOST', '13.209.3.151')
AWS_USER = os.getenv('AWS_USER', 'ubuntu')
AWS_KEY_PATH = os.getenv('AWS_KEY_PATH', r'C:\Users\llll\.ssh\aws-key.pem')
if not os.path.exists(AWS_KEY_PATH) and os.path.exists(r'C:\Users\llll\.ssh\aws-key.pem'):
    AWS_KEY_PATH = r'C:\Users\llll\.ssh\aws-key.pem'
AWS_REMOTE_DIR = os.getenv('AWS_REMOTE_DIR', '/home/ubuntu/ai-auction-experts')
AWS_DOMAIN = os.getenv('AWS_DOMAIN', 'https://ai-auction-experts.cloud')


def run_scp(local_path, remote_dest):
    cmd = [
        'scp', '-o', 'StrictHostKeyChecking=no', '-i', AWS_KEY_PATH,
        local_path, f'{AWS_USER}@{AWS_HOST}:{remote_dest}'
    ]
    print(f"  [SCP] {os.path.basename(local_path)} -> {remote_dest}", flush=True)
    res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if res.returncode != 0:
        raise RuntimeError(f"SCP failed: {res.stderr.strip()}")
    return res.stdout.strip()


def run_ssh(remote_cmd, check=True):
    cmd = [
        'ssh', '-o', 'StrictHostKeyChecking=no', '-i', AWS_KEY_PATH,
        f'{AWS_USER}@{AWS_HOST}', remote_cmd
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if check and res.returncode != 0:
        raise RuntimeError(f"SSH failed (rc={res.returncode}): {res.stderr.strip()}\n{res.stdout.strip()}")
    return res.stdout.strip()


def export_compressed_naver_db(gz_out_path: str):
    tmp_db = gz_out_path.replace('.gz', '')
    if os.path.exists(tmp_db):
        os.remove(tmp_db)

    src = sqlite3.connect(LOCAL_DB_PATH)
    s_cur = src.cursor()
    rows = s_cur.execute("""
        SELECT id, estate_id, address, price, rent, floor, area,
               deal_type, type_detail, lat, lng, estate_type, region, age_info
        FROM naver_real_estate
    """).fetchall()
    src.close()

    dst = sqlite3.connect(tmp_db)
    d_cur = dst.cursor()
    d_cur.execute("""
        CREATE TABLE naver_real_estate (
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
    d_cur.executemany("""
        INSERT INTO naver_real_estate VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    """, rows)
    dst.commit()
    dst.execute("VACUUM;")
    dst.close()

    with open(tmp_db, 'rb') as f_in, gzip.open(gz_out_path, 'wb', compresslevel=6) as f_out:
        shutil.copyfileobj(f_in, f_out)
    os.remove(tmp_db)
    return len(rows), os.path.getsize(gz_out_path)


def verify_live_api():
    ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36"}
    results = []

    # 1. 지도 네이버 매물 마커 오버레이 API 검증
    map_checks = [
        ("서울 마포/성동 아파트 매물마커", "아파트_서울", 37.53, 37.58, 126.90, 127.06),
        ("경기 수원 영통 아파트 매물마커", "아파트_경기", 37.23, 37.28, 127.03, 127.08),
        ("서울 용산/마포 다세대 매물마커", "다세대/빌라_서울", 37.52, 37.57, 126.94, 127.01),
        ("경기 수원/성남 다세대 매물마커", "다세대/빌라_경기", 37.26, 37.46, 126.95, 127.18),
    ]
    for label, etype, min_la, max_la, min_ln, max_ln in map_checks:
        qs = urllib.parse.urlencode({
            "estate_type": etype,
            "min_lat": min_la,
            "max_lat": max_la,
            "min_lng": min_ln,
            "max_lng": max_ln,
        })
        url = f"{AWS_DOMAIN}/api/naver-realestate?{qs}"
        req = urllib.request.Request(url, headers=ua)
        for attempt in range(8):
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    body = json.loads(resp.read().decode('utf-8'))
                    groups = body.get('data', [])
                    total_items = sum(g.get('total_count', 0) for g in groups)
                    results.append(f"  - [{resp.status}] {label}: {len(groups)}개 단지/좌표 (총 {total_items:,}건)")
                    break
            except urllib.error.HTTPError as e:
                if e.code in (502, 503, 504) and attempt < 7:
                    time.sleep(2)
                    continue
                raise

    # 2. 네이버 시세/전세가율 정밀 분석 API (/api/naver_price_analysis) 검증
    analysis_checks = [
        ("서울 마포구 아파트 25평 시세·전세가율", 37.5495, 126.9535, "아파트", 25.5, "10층", "20층", "2016"),
        ("경기 수원 영통구 아파트 25평 시세·전세가율", 37.2458, 127.0461, "아파트", 25.5, "12층", "25층", "2014"),
        ("서울 용산구 다세대/빌라 12평 시세·전세가율", 37.5352, 126.9564, "다세대/빌라", 12.0, "3층", "5층", "2018"),
        ("경기 수원 장안구 연무동 다세대/빌라 15.3평 (2025타경55425)", 37.290885, 127.023138, "다세대", 15.343, "5층", "5층", "25년 이내"),
    ]
    for label, lat, lon, ptype, pyeong, fl, tfl, byear in analysis_checks:
        payload = json.dumps({
            "lat": lat,
            "lon": lon,
            "type": ptype,
            "area_pyeong": pyeong,
            "floor": fl,
            "total_floor": tfl,
            "build_year": byear,
            "appraised_price": 800000000,
            "min_price": 640000000,
            "senior_debt": 0,
            "radius": 1000
        }).encode('utf-8')
        req = urllib.request.Request(
            f"{AWS_DOMAIN}/api/naver_price_analysis",
            data=payload,
            headers={**ua, "Content-Type": "application/json"},
            method="POST"
        )
        for attempt in range(8):
            try:
                with urllib.request.urlopen(req, timeout=20) as resp:
                    body = json.loads(resp.read().decode('utf-8'))
                    calc = body.get('data', {}).get('calculation_result', {})
                    results.append(
                        f"  - [{resp.status}] {label}: 매매사례 {calc.get('sale_count', 0)}건 / "
                        f"전월세사례 {calc.get('rent_count', 0)}건 | "
                        f"추정시세 {calc.get('estimated_market_price_eon', 0)}억 | "
                        f"전세가율 {calc.get('jeonse_ratio', 0)}%"
                    )
                    break
            except urllib.error.HTTPError as e:
                if e.code in (502, 503, 504) and attempt < 7:
                    time.sleep(2)
                    continue
                raise
    return results


def main():
    print("================================================================", flush=True)
    print("🚀 네이버시세 DB & 시세·전세가율 엔진 AWS EC2 안전 배포 (회원·물건 100% 보존)", flush=True)
    print("================================================================", flush=True)

    skip_db = "--skip-db" in sys.argv
    tmp_gz = os.path.join(tempfile.gettempdir(), "naver_sync.db.gz")
    if not skip_db:
        print("[1/4] 로컬 naver_real_estate 테이블 압축 패키징 중...", flush=True)
        row_cnt, gz_size = export_compressed_naver_db(tmp_gz)
        print(f"  ✅ 총 {row_cnt:,}건 매물 압축 완료 ({gz_size / (1024*1024):.2f} MB)", flush=True)
        print("\n[2/4] 압축 DB 및 수정된 분석·적재 스크립트 SCP 전송 중...", flush=True)
        run_scp(tmp_gz, "/tmp/naver_sync.db.gz")
    else:
        print("[1/4] --skip-db 모드: 기존 원격 DB 유지, 코드·캐시·서비스 동기화 진행...", flush=True)
        print("\n[2/4] 수정된 분석·적재 스크립트 SCP 전송 중...", flush=True)

    run_scp(os.path.join(BASE_DIR, "backend", "naver_price_analyzer.py"), f"{AWS_REMOTE_DIR}/backend/naver_price_analyzer.py")
    run_scp(os.path.join(BASE_DIR, "backend", "update_naver_db.py"), f"{AWS_REMOTE_DIR}/backend/update_naver_db.py")
    run_scp(os.path.join(BASE_DIR, "backend", "app.py"), f"{AWS_REMOTE_DIR}/backend/app.py")
    run_scp(os.path.join(BASE_DIR, "public", "map.html"), f"{AWS_REMOTE_DIR}/public/map.html")
    if os.path.exists(tmp_gz):
        os.remove(tmp_gz)

    print("\n[3/4] 원격 서버 naver_real_estate 점검, 구버전 캐시 정리 및 서비스 재기동 중...", flush=True)
    remote_py = f"""{AWS_REMOTE_DIR}/venv/bin/python -c '
import gzip, shutil, sqlite3, os, glob, sys, gc

gz_path = "/tmp/naver_sync.db.gz"
sync_db = "/tmp/naver_sync.db"
remote_dir = "{AWS_REMOTE_DIR}"
main_db = os.path.join(remote_dir, "backend", "data", "map_data.db")

if os.path.exists(gz_path):
    with gzip.open(gz_path, "rb") as f_in, open(sync_db, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

    conn = sqlite3.connect(main_db, timeout=60.0)
    conn.execute("PRAGMA busy_timeout = 60000;")
    cur = conn.cursor()
    cur.execute("ATTACH DATABASE ? AS syncdb", (sync_db,))
    cur.execute("BEGIN IMMEDIATE;")
    try:
        cur.execute("DROP TABLE IF EXISTS main.naver_real_estate;")
        cur.execute(\"\"\"
            CREATE TABLE main.naver_real_estate (
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
            );
        \"\"\")
        cur.execute("INSERT INTO main.naver_real_estate SELECT * FROM syncdb.naver_real_estate;")
        cur.execute("CREATE INDEX idx_naver_estate_id ON naver_real_estate(estate_id);")
        cur.execute("CREATE INDEX idx_naver_type_coords ON naver_real_estate(estate_type, lat, lng);")
        cur.execute("CREATE INDEX idx_naver_region_type_coords ON naver_real_estate(region, estate_type, lat, lng);")
        cur.execute("CREATE INDEX idx_naver_coords ON naver_real_estate(lat, lng);")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
        for p in (gz_path, sync_db):
            if os.path.exists(p):
                os.remove(p)

# 구버전 대용량 피클 캐시 전체 제거 (SQLite BBox 인덱스 직결 조회로 전환되어 메모리 점유 0)
for pattern in (
    os.path.join(remote_dir, "data", "네이버부동산", ".cache_naver_*.pkl"),
    os.path.join(remote_dir, "backend", ".cache_naver_*.pkl"),
):
    for fp in glob.glob(pattern):
        try:
            os.remove(fp)
        except Exception:
            pass

conn2 = sqlite3.connect(main_db)
c2 = conn2.cursor()
for label, sql, params in [
    ("naver_real_estate", "SELECT COUNT(*) FROM naver_real_estate", ()),
    ("apt_seoul_rent", "SELECT COUNT(*) FROM naver_real_estate WHERE region=? AND estate_type=? AND deal_type IN (?,?,?)", ("서울", "아파트", "전세", "월세", "단기임대")),
    ("apt_gyeonggi_rent", "SELECT COUNT(*) FROM naver_real_estate WHERE region=? AND estate_type=? AND deal_type IN (?,?,?)", ("경기", "아파트", "전세", "월세", "단기임대")),
    ("villa_seoul_rent", "SELECT COUNT(*) FROM naver_real_estate WHERE region=? AND estate_type=? AND deal_type IN (?,?,?)", ("서울", "다세대/빌라", "전세", "월세", "단기임대")),
    ("villa_gyeonggi_rent", "SELECT COUNT(*) FROM naver_real_estate WHERE region=? AND estate_type=? AND deal_type IN (?,?,?)", ("경기", "다세대/빌라", "전세", "월세", "단기임대")),
    ("realprice_grids", "SELECT COUNT(*) FROM realprice_grids", ()),
    ("auctions", "SELECT COUNT(*) FROM auctions", ()),
    ("approved_users", "SELECT COUNT(*) FROM approved_users", ()),
    ("board_inquiries", "SELECT COUNT(*) FROM board_inquiries", ()),
]:
    print(f"{{label}}|{{c2.execute(sql, params).fetchone()[0]}}", flush=True)
conn2.close()
' && sudo systemctl restart fastapi.service && sleep 3 && systemctl is-active fastapi.service"""
    ssh_out = run_ssh(remote_py)
    for line in ssh_out.splitlines():
        print(f"  [EC2] {line}", flush=True)

    print("\n[4/4] 운영 도메인(https://ai-auction-experts.cloud) 라이브 네이버시세 API 검증 중...", flush=True)
    for line in verify_live_api():
        print(line, flush=True)

    print("\n🎉 로컬 및 AWS EC2 네이버시세 업데이트가 성공적으로 완료되었습니다!", flush=True)


if __name__ == '__main__':
    main()
