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
    print("=" * 60)
    print("🚀 경공매 업데이트 데이터 & DB AWS EC2 원클릭 배포")
    print("=" * 60)
    print(f"• AWS EC2 호스트 : {AWS_HOST}")
    print(f"• 원격 디렉토리   : {AWS_REMOTE_DIR}")
    print(f"• 라이브 도메인   : {AWS_DOMAIN}")
    print("-" * 60)

    # 1. 엑셀 파일 전송
    excel_local = os.path.join(BASE_DIR, 'data', '경공매업데이트', '경공매데이터_업데이트_대항력추가.xlsx')
    if not os.path.exists(excel_local):
        print(f"❌ 오류: 엑셀 파일이 없습니다: {excel_local}")
        return

    print("\n[1/5] 경공매업데이트 엑셀 파일 전송 중...")
    remote_excel_dir = f"{AWS_REMOTE_DIR}/data/경공매업데이트"
    run_ssh(f"mkdir -p {remote_excel_dir}")
    scp_excel = f'scp -o StrictHostKeyChecking=no -i "{AWS_KEY_PATH}" "{excel_local}" {AWS_USER}@{AWS_HOST}:{remote_excel_dir}/'
    run_cmd(scp_excel)
    print("  엑셀 파일 전송 완료!")

    # 2. 업데이트 스크립트 전송
    script_local = os.path.join(BASE_DIR, 'backend', 'scripts', 'import_auction_data.py')
    print("\n[2/5] import_auction_data.py 스크립트 전송 중...")
    scp_script = f'scp -o StrictHostKeyChecking=no -i "{AWS_KEY_PATH}" "{script_local}" {AWS_USER}@{AWS_HOST}:{AWS_REMOTE_DIR}/backend/scripts/'
    run_cmd(scp_script)
    print("  스크립트 전송 완료!")

    # 3. map_data.db 압축 패키징
    db_local = os.path.join(BASE_DIR, 'backend', 'data', 'map_data.db')
    tar_filename = os.path.join(BASE_DIR, 'map_data_upload.tar.gz')
    print(f"\n[3/5] map_data.db 압축 중 ({tar_filename})...")
    with tarfile.open(tar_filename, "w:gz") as tar:
        tar.add(db_local, arcname="map_data.db")
    tar_size_mb = os.path.getsize(tar_filename) / (1024 * 1024)
    print(f"  압축 완료! 압축 크기: {tar_size_mb:.1f} MB (원본: {os.path.getsize(db_local)/(1024*1024):.1f} MB)")

    # 4. 압축된 DB 전송
    print("\n[4/5] 압축된 DB 파일 서버 전송 중 (SCP)...")
    scp_db = f'scp -o StrictHostKeyChecking=no -i "{AWS_KEY_PATH}" "{tar_filename}" {AWS_USER}@{AWS_HOST}:~/map_data_upload.tar.gz'
    run_cmd(scp_db)
    print("  DB 전송 완료!")

    # 5. 원격 서버 적용 및 서비스 재시작
    print("\n[5/5] 원격 서버 DB 교체 및 서비스 재기동 중...")
    remote_apply_cmds = [
        f"cp {AWS_REMOTE_DIR}/backend/data/map_data.db {AWS_REMOTE_DIR}/backend/data/map_data.db.bak_$(date +%Y%m%d_%H%M%S) 2>/dev/null || true",
        f"tar -xzf ~/map_data_upload.tar.gz -C {AWS_REMOTE_DIR}/backend/data/",
        "rm -f ~/map_data_upload.tar.gz",
        "pkill -f 'python app.py' || true",
        "sleep 1",
        f"bash -c 'cd {AWS_REMOTE_DIR}/backend && nohup ../venv/bin/python app.py > server.log 2>&1 < /dev/null & disown -a; sleep 3'"
    ]
    remote_script = " && ".join(remote_apply_cmds)
    res = run_ssh(remote_script)
    print("  원격 적용 완료! 결과:", res.stdout.strip())

    # 임시 압축파일 삭제
    if os.path.exists(tar_filename):
        try:
            os.remove(tar_filename)
        except Exception:
            pass

    # 원격 DB 확인 및 헬스체크
    print("\n[검증] 원격 서버 상태 확인 중...")
    time.sleep(2)
    verify_cmd = f"sqlite3 {AWS_REMOTE_DIR}/backend/data/map_data.db 'SELECT count(*) FROM auctions;'"
    res_verify = run_ssh(verify_cmd)
    print("  원격 DB 총 물건 수:", res_verify.stdout.strip())

    # 도메인 헬스체크
    try:
        r = requests.get(f"{AWS_DOMAIN}/api/health", timeout=5)
        print(f"  헬스체크 ({AWS_DOMAIN}/api/health): {r.status_code} {r.text[:60]}")
    except Exception as e:
        print(f"  도메인 요청 응답: {e}")

    print("\n🎉 모든 작업이 성공적으로 완료되었습니다!")

if __name__ == '__main__':
    main()
