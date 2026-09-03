# 🌐 AI 경매/공매 시스템 AWS 서버 배포 및 운영 가이드

이 가이드는 로컬에서 실행 중인 AI 경매/공매 분석 시스템을 **AWS 클라우드(EC2)**에 올려 24시간 365일 언제 어디서나 웹 브라우저로 접속할 수 있도록 만드는 완벽 매뉴얼입니다.

---

## 📋 [1단계] AWS EC2 인스턴스 생성

1. **AWS 콘솔 로그인**: [AWS Management Console](https://aws.amazon.com/)에 접속하여 로그인합니다.
2. **EC2 서비스 이동**: 상단 검색창에 **EC2**를 입력하고 이동 후 **[인스턴스 시작 (Launch Instance)]** 버튼을 클릭합니다.
3. **인스턴스 기본 설정**:
   - **이름**: `ai-auction-server` (자유롭게 지정)
   - **애플리케이션 및 OS 이미지 (AMI)**: **Ubuntu Server 22.04 LTS** (또는 24.04 LTS) 선택
   - **인스턴스 유형**:
     - **권장**: `t3.small` (vCPU 2, Mem 2GB - 안정적인 머신러닝/크롤러 구동)
     - **테스트용/프리티어**: `t2.micro` / `t3.micro` (Swap 4GB 자동 설정으로 구동 가능)
   - **키 페어(로그인)**: 기존 키가 없다면 **[새 키 페어 생성]**을 눌러 다운로드(`ai-auction-key.pem`)하여 안전한 폴더에 보관합니다.
4. **네트워크 설정 (보안 그룹)**:
   - **[인터넷에서 HTTP/HTTPS 트래픽 허용]** 체크박스 2개 모두 체크
   - **[편집]**을 눌러 아래 인바운드 규칙이 포함되었는지 확인합니다:
     | 유형 | 프로토콜 | 포트 범위 | 소스 | 설명 |
     | :--- | :--- | :--- | :--- | :--- |
     | **SSH** | TCP | `22` | 내 IP 또는 위치 무관 (0.0.0.0/0) | 원격 터미널 접속 |
     | **HTTP** | TCP | `80` | 위치 무관 (0.0.0.0/0) | 웹 서비스 기본 포트 |
     | **HTTPS** | TCP | `443` | 위치 무관 (0.0.0.0/0) | SSL 암호화 웹 포트 |
     | **사용자 지정 TCP** | TCP | `8001` | 위치 무관 (0.0.0.0/0) | 백엔드 API/대시보드 직통 포트 |
5. **스토리지 구성**: 기본 8GB ➡️ **20GB ~ 30GB (gp3)**로 넉넉하게 설정 후 **[인스턴스 시작]**을 누릅니다.

---

## 💻 [2단계] 서버 접속 및 원클릭 설치 (3줄 명령어)

### 1. SSH를 통해 EC2 터미널 접속
Windows 터미널(PowerShell) 또는 명령 프롬프트를 열고 다운로드한 키페어가 있는 위치에서 접속합니다:
```bash
ssh -i "C:\경로\ai-auction-key.pem" ubuntu@<서버_공인_IP>
```
*(예: `ssh -i ai-auction-key.pem ubuntu@13.125.100.200`)*

### 2. 저장소 복제 및 원클릭 설치 스크립트 실행
서버 터미널에 아래 명령어를 **한 줄씩 입력**합니다:

```bash
# 1. GitHub에서 코드 내려받기
git clone https://github.com/h80494-netizen/ai-auction-experts.git

# 2. 프로젝트 디렉토리로 이동
cd ai-auction-experts

# 3. 배포 초기화 스크립트 실행 (Docker, Swap 4GB, 방화벽, 컨테이너 가동 자동 완료)
chmod +x setup_aws_ec2.sh deploy.sh
./setup_aws_ec2.sh
```

> **스크립트가 자동으로 수행하는 작업:**
> - 4GB Swap 메모리 생성 (메모리 부족 에러 방지)
> - Docker & Docker-Compose 최신 버전 설치
> - 필요한 포트(80, 443, 8001) 방화벽 개방
> - Docker 컨테이너 빌드 및 백그라운드 자동 상시 가동

---

## 📦 [3단계] 데이터베이스(DB) 및 환경변수 전송

실거래가 분석 격자 DB(`backend/data/map_data.db`)와 API 키가 들어있는 `.env` 파일을 서버로 전송합니다.

### 방법 1. 로컬(내 컴퓨터)에서 `sync_data_to_ec2.bat` 더블클릭
1. 프로젝트 폴더의 [sync_data_to_ec2.bat](file:///c:/Users/llll/Documents/두인경매/바이브코딩/sync_data_to_ec2.bat) 파일을 실행합니다.
2. 화면의 안내에 따라 **서버 IP**와 **키페어(.pem) 파일 경로**를 입력하면 자동으로 업로드됩니다.

### 방법 2. 직접 scp 명령어 실행 (내 PC 터미널에서)
```bash
# .env 파일 전송
scp -i "ai-auction-key.pem" backend/.env ubuntu@<서버_공인_IP>:~/ai-auction-experts/backend/.env

# SQLite DB 파일 전송
scp -i "ai-auction-key.pem" -r backend/data/* ubuntu@<서버_공인_IP>:~/ai-auction-experts/backend/data/
```

전송 후 서버에서 서비스를 재시작합니다:
```bash
sudo docker compose restart
```

---

## 🌐 [4단계] 브라우저 접속 확인

웹 브라우저를 열고 주소창에 서버 IP를 입력합니다:
- 👉 **`http://<서버_공인_IP>`** (기본 80 포트로 바로 연결됩니다)
- 👉 **`http://<서버_공인_IP>:8001`**

지도가 선명하게 뜨고 경매/공매 분석 대시보드가 정상 작동하는 것을 확인할 수 있습니다! 🎉

---

## 🛠️ [5단계] 유지보수 및 유용한 명령어

### 1. 코드 수정 후 서버 업데이트 (재배포)
서버 터미널에서 아래 명령어 하나만 입력하면 최신 코드를 당겨와 즉시 재빌드/재시작합니다:
```bash
./deploy.sh
```

### 2. 실시간 서버 로그 확인
```bash
sudo docker compose logs -f
```

### 3. 서버 중지 및 재시작
```bash
# 중지
sudo docker compose down

# 시작
sudo docker compose up -d

# 재시작
sudo docker compose restart
```

---

## 🔒 [보너스] 무료 도메인 연결 및 SSL(HTTPS) 인증서 적용

만약 `https://내도메인.com` 형태로 보안 인증서를 적용하고 싶으시다면 Caddy 또는 Nginx Certbot을 사용하면 1분 만에 완료됩니다:

```bash
# Caddy 설치
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLF 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLF 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy

# Caddy 설정 (/etc/caddy/Caddyfile)
# my-auction-domain.com {
#     reverse_proxy localhost:8001
# }

# Caddy 재시작 (Let's Encrypt SSL 자동 발급)
sudo systemctl restart caddy
```
