#!/bin/bash
set -e

echo "=========================================================="
echo "🚀 AWS EC2 AI 경매/공매 시스템 원클릭 배포 환경 초기화"
echo "=========================================================="

# 1. 시스템 패키지 업데이트 및 필수 툴 설치
echo "[1/5] 시스템 패키지 업데이트 중..."
sudo apt-get update -y
sudo apt-get install -y ca-certificates curl gnupg lsb-release git ufw

# 2. Swap 메모리 4GB 설정 (빌드 및 머신러닝/지리데이터 처리 시 OOM 방지)
if [ ! -f /swapfile ]; then
    echo "[2/5] 4GB Swap 메모리 생성 중 (메모리 안정성 확보)..."
    sudo fallocate -l 4G /swapfile || sudo dd if=/dev/zero of=/swapfile bs=1M count=4096
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    echo "  Swap 메모리 4GB 활성화 완료!"
else
    echo "[2/5] Swap 메모리가 이미 설정되어 있습니다."
fi

# 3. Docker & Docker Compose 공식 저장소 설치
echo "[3/5] Docker 및 Docker Compose 설치 중..."
if ! command -v docker &> /dev/null; then
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt-get update -y
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # 현재 유저를 docker 그룹에 등록 (sudo 없이 docker 실행 가능)
    sudo usermod -aG docker $USER
    echo "  Docker 설치 완료!"
else
    echo "  Docker가 이미 설치되어 있습니다."
fi

# 4. 방화벽 설정 (22, 80, 443, 8001 포트 허용)
echo "[4/5] 방화벽 포트 설정 중..."
sudo ufw allow 22/tcp || true
sudo ufw allow 80/tcp || true
sudo ufw allow 443/tcp || true
sudo ufw allow 8001/tcp || true
sudo ufw --force enable || true

# 5. Docker Compose를 통한 서비스 빌드 및 가동
echo "[5/5] Docker 컨테이너 빌드 및 가동 중..."
sudo docker compose down || true
sudo docker compose build
sudo docker compose up -d

echo ""
echo "=========================================================="
echo "🎉 AWS 서버 배포가 성공적으로 완료되었습니다!"
echo "웹 브라우저에서 아래 주소로 접속해 보세요:"
echo "👉 http://$(curl -s ifconfig.me):80 (또는 포트 없이 http://$(curl -s ifconfig.me))"
echo "👉 http://$(curl -s ifconfig.me):8001"
echo "=========================================================="
