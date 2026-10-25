import os
import sys
import subprocess
import time
import tarfile
import requests
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

def run_cmd(cmd, check=True):
    print(f"  [RUN] {cmd}")
    res = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if check and res.returncode != 0:
        print(f"  [ERROR] {res.stderr.strip()}")
        raise RuntimeError(f"Command failed: {res.stderr.strip()}")
    return res.stdout.strip()

def run_ssh(remote_cmd):
    ssh_cmd = f'ssh -o StrictHostKeyChecking=no -i "{AWS_KEY_PATH}" {AWS_USER}@{AWS_HOST} "{remote_cmd}"'
    res = subprocess.run(ssh_cmd, shell=True, text=True, capture_output=True)
    if res.returncode != 0:
        print(f"  [SSH ERROR] {res.stderr.strip()}")
    return res

def main():
    print("=" * 65)
    print("🚀 네이버 전월세 DB & 시세분석 로직 수정 AWS EC2 원클릭 배포")
    print("=" * 65)
    print(f"• AWS EC2 호스트 : {AWS_HOST}")
    print(f"• 원격 디렉토리   : {AWS_REMOTE_DIR}")
    print(f"• 라이브 도메인   : {AWS_DOMAIN}")
    print("-" * 65)

    # 1. 수정된 코드 파일 전송
    print("\n[1/4] 수정된 코드 및 웹 프론트엔드 파일 전송 중...")
    files_to_send = [
        (os.path.join(BASE_DIR, 'backend', 'naver_price_analyzer.py'), f"{AWS_REMOTE_DIR}/backend/"),
        (os.path.join(BASE_DIR, 'backend', 'update_naver_db.py'), f"{AWS_REMOTE_DIR}/backend/"),
        (os.path.join(BASE_DIR, 'public', 'map.html'), f"{AWS_REMOTE_DIR}/public/"),
    ]
    for local_f, remote_dest in files_to_send:
        if os.path.exists(local_f):
            scp_cmd = f'scp -o StrictHostKeyChecking=no -i "{AWS_KEY_PATH}" "{local_f}" {AWS_USER}@{AWS_HOST}:{remote_dest}'
            run_cmd(scp_cmd)
            print(f"  ✓ {os.path.basename(local_f)} 전송 완료")
        else:
            print(f"  ⚠️ 파일 없음: {local_f}")

    # 2. 통합 DB(map_data.db) 압축 패키징
    db_local = os.path.join(BASE_DIR, 'backend', 'data', 'map_data.db')
    if not os.path.exists(db_local):
        print(f"❌ DB 파일이 없습니다: {db_local}")
        return

    tar_filename = os.path.join(BASE_DIR, 'map_data_naver_upload.tar.gz')
    print(f"\n[2/4] map_data.db 압축 중 ({tar_filename})...")
    with tarfile.open(tar_filename, "w:gz") as tar:
        tar.add(db_local, arcname="map_data.db")
    tar_size_mb = os.path.getsize(tar_filename) / (1024 * 1024)
    print(f"  압축 완료! 압축 크기: {tar_size_mb:.1f} MB (원본: {os.path.getsize(db_local)/(1024*1024):.1f} MB)")

    # 3. 압축된 DB 파일 SCP 전송
    print("\n[3/4] 압축된 DB 파일 서버 전송 중 (SCP)...")
    scp_db = f'scp -o StrictHostKeyChecking=no -i "{AWS_KEY_PATH}" "{tar_filename}" {AWS_USER}@{AWS_HOST}:~/map_data_upload.tar.gz'
    run_cmd(scp_db)
    print("  DB 전송 완료!")

    # 4. 원격 서버 적용 및 서비스 재기동
    print("\n[4/4] 원격 서버 DB 교체 및 캐시 초기화, 서비스 재기동 중...")
    remote_apply_cmds = [
        f"cp {AWS_REMOTE_DIR}/backend/data/map_data.db {AWS_REMOTE_DIR}/backend/data/map_data.db.bak_$(date +%Y%m%d_%H%M%S) 2>/dev/null || true",
        f"tar -xzf ~/map_data_upload.tar.gz -C {AWS_REMOTE_DIR}/backend/data/",
        "rm -f ~/map_data_upload.tar.gz",
        # 이전 시세 분석 캐시 pkl 파일 제거 (새 DB 및 새 로직 즉시 반영)
        f"rm -f {AWS_REMOTE_DIR}/backend/.cache_naver_*.pkl 2>/dev/null || true",
        "pkill -f 'python app.py' || true",
        "sleep 1",
        f"bash -c 'cd {AWS_REMOTE_DIR}/backend && nohup ../venv/bin/python app.py > server.log 2>&1 < /dev/null & disown -a; sleep 3'"
    ]
    remote_script = " && ".join(remote_apply_cmds)
    res = run_ssh(remote_script)
    print("  원격 서비스 재기동 완료!")

    # 임시 압축파일 삭제
    if os.path.exists(tar_filename):
        try:
            os.remove(tar_filename)
        except Exception:
            pass

    # 검증 1: 원격 DB 레코드 통계
    print("\n[검증 1] 원격 DB 네이버 매물 거래유형별 통계 확인 중...")
    time.sleep(2)
    verify_cmd = f"sqlite3 {AWS_REMOTE_DIR}/backend/data/map_data.db \"SELECT deal_type, count(*) FROM naver_real_estate GROUP BY deal_type;\""
    res_verify = run_ssh(verify_cmd)
    print("  원격 DB 거래유형별 통계:\n" + res_verify.stdout.strip())

    # 검증 2: 도메인 헬스체크
    print("\n[검증 2] 라이브 도메인 헬스체크...")
    try:
        r = requests.get(f"{AWS_DOMAIN}/api/health", timeout=5)
        print(f"  헬스체크 ({AWS_DOMAIN}/api/health): {r.status_code} {r.text[:60]}")
    except Exception as e:
        print(f"  도메인 요청 응답: {e}")

    print("\n🎉 AWS 배포 및 서비스 재기동이 성공적으로 완료되었습니다!")

if __name__ == '__main__':
    main()
