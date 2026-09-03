import os
import sys
import subprocess
import time
import io
import requests
from dotenv import load_dotenv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 로컬 루트 및 .env 로드
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))
load_dotenv(os.path.join(BASE_DIR, 'backend', '.env'))

AWS_HOST = os.getenv('AWS_HOST', '13.209.3.151')
AWS_USER = os.getenv('AWS_USER', 'ubuntu')
AWS_KEY_PATH = os.getenv('AWS_KEY_PATH', r'C:\Users\llll\Downloads\aws-key.pem')
AWS_REMOTE_DIR = os.getenv('AWS_REMOTE_DIR', '/home/ubuntu/ai-auction-experts')
AWS_DOMAIN = os.getenv('AWS_DOMAIN', 'https://ai-auction-experts.cloud')

def run_cmd(cmd, check=True):
    """로컬 셸 명령어를 실행합니다."""
    print(f"  [RUN] {cmd}")
    res = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if check and res.returncode != 0:
        print(f"  [ERROR] {res.stderr.strip()}")
        raise RuntimeError(f"Command failed with exit code {res.returncode}")
    return res.stdout.strip()

def run_ssh(remote_cmd):
    """AWS EC2 서버에서 원격 SSH 명령어를 실행합니다."""
    ssh_cmd = f'ssh -o StrictHostKeyChecking=no -i "{AWS_KEY_PATH}" {AWS_USER}@{AWS_HOST} "{remote_cmd}"'
    return subprocess.run(ssh_cmd, shell=True, text=True, capture_output=True)

def main():
    print("==========================================================")
    print("🚀 AWS EC2 서버 자동 배포 시스템 (.env 연동)")
    print("==========================================================")
    print(f"• 대상 서버 IP : {AWS_HOST}")
    print(f"• 접속 계정    : {AWS_USER}")
    print(f"• 키페어 경로  : {AWS_KEY_PATH}")
    print(f"• 원격 디렉토리: {AWS_REMOTE_DIR}")
    print(f"• 라이브 도메인: {AWS_DOMAIN}")
    print("----------------------------------------------------------")

    if not os.path.exists(AWS_KEY_PATH):
        print(f"❌ 오류: 키페어 파일({AWS_KEY_PATH})을 찾을 수 없습니다. .env 경로를 확인해주세요.")
        sys.exit(1)

    with_db = '--with-db' in sys.argv or '-db' in sys.argv
    if with_db:
        print("📦 [모드] 전체 동기화 모드 (소스코드 + 대용량 데이터베이스 포함)")
    else:
        print("⚡ [모드] 초고속 코드 동기화 모드 (소스코드 및 정적 파일 즉시 배포)")
        print("   (DB까지 함께 올리려면 'python deploy_to_aws.py --with-db'를 실행하세요)")

    # 1. 아카이브 생성 (Python tarfile 모듈 활용 - 초고속)
    tar_filename = "deploy_auto.tar.gz"
    print(f"\n[1/4] 배포 패키지 스마트 압축 중 ({tar_filename})...")
    
    import tarfile

    def filter_func(tarinfo):
        name = tarinfo.name
        # 무조건 제외할 파일/폴더
        if '__pycache__' in name or name.endswith('.pyc') or name.endswith('.log') or 'cloudflared' in name or '.git' in name or 'scratch' in name or 'downloads' in name or 'node_modules' in name:
            return None
        if not with_db:
            if name.endswith('.db') or name.endswith('.db-wal') or name.endswith('.db-shm') or name.endswith('.pkl'):
                return None
        return tarinfo

    with tarfile.open(tar_filename, "w:gz") as tar:
        for item in ["backend", "public", "requirements.txt", ".env"]:
            if os.path.exists(item):
                tar.add(item, filter=filter_func)
                
    pkg_size_mb = os.path.getsize(tar_filename) / (1024 * 1024)
    print(f"  스마트 압축 완료! 패키지 크기: {pkg_size_mb:.2f} MB")

    # 2. 서버로 파일 전송 (SCP)
    print(f"\n[2/4] AWS 서버로 패키지 전송 중 (SCP)...")
    scp_cmd = f'scp -o StrictHostKeyChecking=no -i "{AWS_KEY_PATH}" {tar_filename} {AWS_USER}@{AWS_HOST}:~/{tar_filename}'
    run_cmd(scp_cmd)
    print("  전송 완료!")

    # 3. 원격 서버에서 압축 해제 및 서비스 재시작
    print(f"\n[3/4] 원격 서버 적용 및 서비스 무중단 재시작 중...")
    remote_script = f"cd {AWS_REMOTE_DIR} && tar -xzf ~/{tar_filename} && rm -f ~/{tar_filename} && pkill -f 'ai-auction-experts/venv/bin/python' || true; sleep 1; cd {AWS_REMOTE_DIR}/backend && nohup ../venv/bin/python app.py > server.log 2>&1 &"
    res = run_ssh(remote_script)
    print("  서버 프로세스 재가동 완료!")

    # 임시 압축파일 삭제
    if os.path.exists(tar_filename):
        os.remove(tar_filename)

    # 4. 라이브 헬스체크 검증
    print(f"\n[4/4] 라이브 서비스 헬스체크 검증 중 ({AWS_DOMAIN})...")
    time.sleep(3)
    try:
        check_url = f"{AWS_DOMAIN}/map.html"
        resp = requests.get(check_url, timeout=10)
        if resp.status_code == 200:
            print(f"  ✅ {AWS_DOMAIN} 접속 성공 (HTTP 200 OK)")
            print(f"  ✅ 실거래가 격자 지도 및 분석 시스템이 정상 가동 중입니다!")
        else:
            print(f"  ⚠️ 응답 상태 코드: {resp.status_code}")
    except Exception as e:
        print(f"  ⚠️ 헬스체크 요청 확인 중: {e}")

    print("\n==========================================================")
    print("🎉 AWS 서버 자동 배포가 성공적으로 완료되었습니다!")
    print(f"👉 웹 브라우저 접속: {AWS_DOMAIN}")
    print("==========================================================")

if __name__ == '__main__':
    main()
