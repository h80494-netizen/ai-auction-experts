#!/bin/bash
set -e

echo "=========================================================="
echo "🔄 최신 코드 수신 및 무중단 재배포 실행 중..."
echo "=========================================================="

# 1. Git 최신 변경사항 pull
echo "[1/3] Git 최신 코드 동기화 중..."
git pull origin main || git pull

# 2. Docker 이미지 재빌드
echo "[2/3] Docker 컨테이너 재빌드 중..."
sudo docker compose build

# 3. 컨테이너 재시작
echo "[3/3] 서비스 재시작 중..."
sudo docker compose up -d

echo ""
echo "✅ 배포가 성공적으로 완료되었습니다!"
echo "서버 상태 확인: sudo docker compose ps"
echo "실시간 로그 확인: sudo docker compose logs -f"
