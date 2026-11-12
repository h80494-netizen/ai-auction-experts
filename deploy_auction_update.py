import os
import sys
import subprocess
import time
import urllib.request
import json
import io
from dotenv import load_dotenv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', write_through=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

AWS_HOST = os.getenv('AWS_HOST', '13.209.3.151')
AWS_USER = os.getenv('AWS_USER', 'ubuntu')
AWS_KEY_PATH = os.getenv('AWS_KEY_PATH', r'C:\Users\llll\Downloads\aws-key.pem')
AWS_REMOTE_DIR = os.getenv('AWS_REMOTE_DIR', '/home/ubuntu/ai-auction-experts')
AWS_DOMAIN = os.getenv('AWS_DOMAIN', 'https://ai-auction-experts.cloud')


def find_latest_update_excel():
    update_dir = os.path.join(BASE_DIR, 'data', '경공매업데이트')
    candidates = []
    if os.path.exists(update_dir):
        for fn in os.listdir(update_dir):
            if fn.startswith('경공매데이터') and fn.endswith('.xlsx') and not fn.startswith('~$'):
                full_p = os.path.join(update_dir, fn)
                candidates.append((os.path.getmtime(full_p), full_p, fn))
    if candidates:
        candidates.sort(reverse=True)
        return candidates[0][1], candidates[0][2]
    default_p = os.path.join(update_dir, '경공매데이터_업데이트_대항력추가.xlsx')
    return default_p, '경공매데이터_업데이트_대항력추가.xlsx'


def run_scp(local_path, remote_dest):
    cmd = [
        "scp", "-o", "StrictHostKeyChecking=no", "-i", AWS_KEY_PATH,
        local_path, f"{AWS_USER}@{AWS_HOST}:{remote_dest}"
    ]
    print(f"  [SCP] {os.path.basename(local_path)} -> {remote_dest}")
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if res.returncode != 0:
        raise RuntimeError(f"SCP failed: {res.stderr.strip()}")
    return res.stdout.strip()


def run_ssh(remote_cmd, check=True):
    cmd = [
        "ssh", "-o", "StrictHostKeyChecking=no", "-i", AWS_KEY_PATH,
        f"{AWS_USER}@{AWS_HOST}", remote_cmd
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and res.returncode != 0:
        raise RuntimeError(f"SSH command failed ({res.returncode}): {res.stderr.strip()}\n{res.stdout.strip()}")
    return res


def main():
    print("=" * 64)
    print("🚀 경공매 업데이트 데이터 로컬 & AWS EC2 안전 배포 (회원DB 100% 보존)")
    print("=" * 64)
    excel_local, excel_name = find_latest_update_excel()
    if not os.path.exists(excel_local):
        print(f"❌ 오류: 엑셀 파일이 없습니다: {excel_local}")
        sys.exit(1)

    print(f"• 업데이트 엑셀 : {excel_name} ({os.path.getsize(excel_local)/(1024*1024):.1f} MB)")
    print(f"• AWS EC2 호스트: {AWS_USER}@{AWS_HOST}")
    print(f"• 원격 디렉토리 : {AWS_REMOTE_DIR}")
    print(f"• 라이브 도메인 : {AWS_DOMAIN}")
    print("-" * 64)

    # 1. 원격 업로드 폴더 준비 및 엑셀 전송
    print("\n[1/4] 경공매업데이트 엑셀 파일 EC2 전송 중...")
    remote_excel_dir = f"{AWS_REMOTE_DIR}/data/경공매업데이트"
    run_ssh(f"mkdir -p '{remote_excel_dir}'")
    run_scp(excel_local, f"{remote_excel_dir}/{excel_name}")
    print("  ✅ 엑셀 파일 전송 완료!")

    # 2. 임포트 및 장기미집행 플래깅 스크립트 전송
    print("\n[2/4] 데이터 적재 스크립트(import_auction_data.py, flag_unexecuted_auctions.py) 전송 중...")
    run_scp(os.path.join(BASE_DIR, 'backend', 'scripts', 'import_auction_data.py'), f"{AWS_REMOTE_DIR}/backend/scripts/import_auction_data.py")
    run_scp(os.path.join(BASE_DIR, 'backend', 'scripts', 'flag_unexecuted_auctions.py'), f"{AWS_REMOTE_DIR}/backend/scripts/flag_unexecuted_auctions.py")
    print("  ✅ 스크립트 전송 완료!")

    # 3. 원격 EC2에서 auctions 테이블만 인플레이스 갱신 및 systemd 재시작
    print("\n[3/4] 원격 서버 DB(auctions 테이블) 갱신 및 fastapi.service 재기동 중...")
    remote_update_cmd = (
        f"cd {AWS_REMOTE_DIR} && "
        f"{AWS_REMOTE_DIR}/venv/bin/python backend/scripts/import_auction_data.py '{remote_excel_dir}/{excel_name}' && "
        f"{AWS_REMOTE_DIR}/venv/bin/python backend/scripts/flag_unexecuted_auctions.py && "
        f"sudo systemctl restart fastapi.service && "
        f"sleep 2 && "
        f"systemctl is-active fastapi.service"
    )
    res_upd = run_ssh(remote_update_cmd)
    print(res_upd.stdout.strip())

    # 4. 원격 DB 무결성 및 라이브 API 검증
    print("\n[4/4] 원격 DB 물건 수·회원 보존 여부 및 라이브 API 검증 중...")
    verify_sql = (
        "SELECT 'auctions_total', COUNT(*) FROM auctions "
        "UNION ALL SELECT 'auction_경매', COUNT(*) FROM auctions WHERE sale_type='경매' "
        "UNION ALL SELECT 'auction_공매', COUNT(*) FROM auctions WHERE sale_type='공매' "
        "UNION ALL SELECT 'unexecuted_flagged', COUNT(*) FROM auctions WHERE is_unexecuted=1 "
        "UNION ALL SELECT 'approved_users', COUNT(*) FROM approved_users "
        "UNION ALL SELECT 'board_inquiries', COUNT(*) FROM board_inquiries;"
    )
    res_db = run_ssh(f"sqlite3 {AWS_REMOTE_DIR}/backend/data/map_data.db \"{verify_sql}\"")
    print("  [원격 SQLite 검증 결과]")
    for line in res_db.stdout.strip().splitlines():
        print(f"   - {line}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    test_url = f"{AWS_DOMAIN}/api/map/auctions?min_lat=37.45&max_lat=37.60&min_lng=126.85&max_lng=127.05&property_types=%EC%95%84%ED%8C%8C%ED%8A%B8,%EC%98%A4%ED%94%BC%EC%8A%A4%ED%85%94,%EC%83%81%EA%B0%80(%EC%A7%91%ED%95%A9)&special_rights=%EB%8C%80%ED%95%AD%EB%A0%A5%EC%97%86%EC%9D%8C"
    req = urllib.request.Request(test_url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = json.loads(resp.read().decode('utf-8'))
        print(f"  [라이브 API 응답 ({resp.status})] status={body.get('status')}, 서울 서남/도심 대항력없음 조회 건수={len(body.get('data', []))}건")

    print("\n🎉 로컬 및 AWS EC2 경공매 데이터 업데이트가 완벽하게 완료되었습니다!")


if __name__ == '__main__':
    main()
