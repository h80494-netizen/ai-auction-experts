import os
import sys
import io
import gzip
import shutil
import sqlite3
import tempfile
import subprocess
import urllib.request
import urllib.parse
import json
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
AWS_KEY_PATH = os.getenv('AWS_KEY_PATH', r'C:\Users\llll\Downloads\aws-key.pem')
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


def export_compressed_realprice_db(gz_out_path: str):
    tmp_db = gz_out_path.replace('.gz', '')
    if os.path.exists(tmp_db):
        os.remove(tmp_db)

    src = sqlite3.connect(LOCAL_DB_PATH)
    s_cur = src.cursor()
    rows = s_cur.execute("""
        SELECT lat_idx, lng_idx, property_type, lat, lng,
               avg_price_per_pyeong, avg_deposit_per_pyeong, avg_rent,
               jeonse_ratio, transaction_count, sale_count, rent_count,
               age_premium_ratio, floor_sensitivity,
               sales_count_under_10, sales_count_10_to_20, sales_count_20_to_30, sales_count_over_30,
               sale_price_change_rate, rent_price_change_rate, new_build_price, old_build_price
        FROM realprice_grids
    """).fetchall()
    src.close()

    dst = sqlite3.connect(tmp_db)
    d_cur = dst.cursor()
    d_cur.execute("""
        CREATE TABLE realprice_grids (
            lat_idx INTEGER,
            lng_idx INTEGER,
            property_type TEXT,
            lat REAL,
            lng REAL,
            avg_price_per_pyeong REAL,
            avg_deposit_per_pyeong REAL,
            avg_rent REAL,
            jeonse_ratio REAL,
            transaction_count INTEGER,
            sale_count INTEGER,
            rent_count INTEGER,
            age_premium_ratio REAL,
            floor_sensitivity REAL,
            sales_count_under_10 INTEGER,
            sales_count_10_to_20 INTEGER,
            sales_count_20_to_30 INTEGER,
            sales_count_over_30 INTEGER,
            sale_price_change_rate REAL,
            rent_price_change_rate REAL,
            new_build_price REAL DEFAULT 0,
            old_build_price REAL DEFAULT 0,
            PRIMARY KEY (lat_idx, lng_idx, property_type)
        )
    """)
    d_cur.executemany("""
        INSERT INTO realprice_grids VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
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
    checks = [
        ("서울 강남 아파트", 37.48, 37.53, 127.01, 127.07, "아파트"),
        ("서울 강남 상업업무용", 37.48, 37.53, 127.01, 127.07, "상업업무용"),
        ("경기 화성/수원 아파트", 37.19, 37.30, 126.98, 127.12, "아파트"),
        ("인천 연수/남동 오피스텔", 37.38, 37.47, 126.63, 126.74, "오피스텔"),
        ("충남 천안/아산 아파트", 36.76, 36.86, 127.08, 127.18, "아파트"),
        ("강원 원주/춘천 아파트", 37.31, 37.38, 127.91, 127.99, "아파트"),
        ("강원 강릉 토지", 37.72, 37.82, 128.85, 128.95, "토지"),
    ]
    results = []
    for label, min_la, max_la, min_ln, max_ln, ptype in checks:
        qs = urllib.parse.urlencode({
            "min_lat": min_la,
            "max_lat": max_la,
            "min_lng": min_ln,
            "max_lng": max_ln,
            "property_type": ptype,
            "indicator_type": "avg_price_per_pyeong",
            "grid_size": 1000
        })
        url = f"{AWS_DOMAIN}/api/map/realprice_indicators?{qs}"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36"
        })
        for attempt in range(8):
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    body = json.loads(resp.read().decode('utf-8'))
                    cnt = len(body.get('data', []))
                    results.append(f"  - [{resp.status}] {label} ({ptype}): {cnt}개 격자 정상 반환")
                    break
            except urllib.error.HTTPError as e:
                if e.code in (502, 503, 504) and attempt < 7:
                    import time
                    time.sleep(2)
                    continue
                raise
    return results


def main():
    print("================================================================", flush=True)
    print("🚀 실거래가 격자 오버레이 AWS EC2 안전 배포 (회원·물건 DB 100% 보존)", flush=True)
    print("================================================================", flush=True)

    tmp_gz = os.path.join(tempfile.gettempdir(), "realprice_sync.db.gz")
    print("[1/4] 로컬 realprice_grids 압축 패키징 중...", flush=True)
    row_cnt, gz_size = export_compressed_realprice_db(tmp_gz)
    print(f"  ✅ 총 {row_cnt:,}개 격자 압축 완료 ({gz_size / (1024*1024):.2f} MB)", flush=True)

    print("\n[2/4] 압축 격자 DB 및 최신 load_realprice_data.py 전송 중...", flush=True)
    run_scp(tmp_gz, "/tmp/realprice_sync.db.gz")
    run_scp(os.path.join(BASE_DIR, "backend", "load_realprice_data.py"), f"{AWS_REMOTE_DIR}/backend/load_realprice_data.py")
    if os.path.exists(tmp_gz):
        os.remove(tmp_gz)

    print("\n[3/4] 원격 서버 map_data.db 내 realprice_grids 인플레이스 교체 및 재기동 중...", flush=True)
    remote_py = f"""python3 -c '
import gzip, shutil, sqlite3, os

gz_path = "/tmp/realprice_sync.db.gz"
sync_db = "/tmp/realprice_sync.db"
main_db = "{AWS_REMOTE_DIR}/backend/data/map_data.db"

with gzip.open(gz_path, "rb") as f_in, open(sync_db, "wb") as f_out:
    shutil.copyfileobj(f_in, f_out)

conn = sqlite3.connect(main_db, timeout=60.0)
conn.execute("PRAGMA busy_timeout = 60000;")
cur = conn.cursor()
cur.execute("ATTACH DATABASE ? AS syncdb", (sync_db,))
cur.execute("BEGIN IMMEDIATE;")
try:
    cur.execute("DROP TABLE IF EXISTS main.realprice_grids;")
    cur.execute(\"\"\"
        CREATE TABLE main.realprice_grids (
            lat_idx INTEGER,
            lng_idx INTEGER,
            property_type TEXT,
            lat REAL,
            lng REAL,
            avg_price_per_pyeong REAL,
            avg_deposit_per_pyeong REAL,
            avg_rent REAL,
            jeonse_ratio REAL,
            transaction_count INTEGER,
            sale_count INTEGER,
            rent_count INTEGER,
            age_premium_ratio REAL,
            floor_sensitivity REAL,
            sales_count_under_10 INTEGER,
            sales_count_10_to_20 INTEGER,
            sales_count_20_to_30 INTEGER,
            sales_count_over_30 INTEGER,
            sale_price_change_rate REAL,
            rent_price_change_rate REAL,
            new_build_price REAL DEFAULT 0,
            old_build_price REAL DEFAULT 0,
            PRIMARY KEY (lat_idx, lng_idx, property_type)
        );
    \"\"\")
    cur.execute("INSERT INTO main.realprice_grids SELECT * FROM syncdb.realprice_grids;")
    cur.execute("CREATE INDEX idx_realprice_grids_type_lat_lng ON realprice_grids(property_type, lat, lng);")
    conn.commit()
except Exception:
    conn.rollback()
    raise
finally:
    conn.close()
    for p in (gz_path, sync_db):
        if os.path.exists(p):
            os.remove(p)

conn2 = sqlite3.connect(main_db)
c2 = conn2.cursor()
for label, sql in [
    ("realprice_grids", "SELECT COUNT(*) FROM realprice_grids"),
    ("realprice_tx_sum", "SELECT SUM(transaction_count) FROM realprice_grids"),
    ("auctions", "SELECT COUNT(*) FROM auctions"),
    ("approved_users", "SELECT COUNT(*) FROM approved_users"),
    ("board_inquiries", "SELECT COUNT(*) FROM board_inquiries"),
]:
    print(f"{{label}}|{{c2.execute(sql).fetchone()[0]}}")
conn2.close()
' && sudo systemctl restart fastapi.service && sleep 2 && systemctl is-active fastapi.service"""
    ssh_out = run_ssh(remote_py)
    for line in ssh_out.splitlines():
        print(f"  [EC2] {line}", flush=True)

    print("\n[4/4] 운영 도메인(https://ai-auction-experts.cloud) 5개 시도 라이브 API 검증 중...", flush=True)
    for line in verify_live_api():
        print(line, flush=True)

    print("\n🎉 로컬 및 AWS EC2 실거래가 격자 오버레이 업데이트가 완료되었습니다!", flush=True)


if __name__ == '__main__':
    main()

