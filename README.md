# 🏛️ AI Auction Expert 2.0 (인공지능 부동산 경·공매 통합 분석 시스템)

> **20년 경력 실전 경매 전문가 사고모델 탑재**  
> 대법원 법원경매 및 온비드(KAMCO) 공매 데이터를 실시간 수집·분석하고, 국토교통부 공적장부(V-World), SGIS 인구통계, 네이버 실거래 시세를 융합하여 10단계 심층 권리분석 및 맞춤형 투자 보고서를 자동 생성하는 종합 플랫폼입니다.

---

## 📌 주요 기능
- **통합 물건 스크래핑**: 대법원 경매 사건번호(타경) 및 온비드 공매 관리번호를 기반으로 물건 현황, 감정평가서, 매각물건명세서 등 필수 서류 실시간 추출
- **Gemini AI 10단계 심층 권리분석**: 말소기준권리 판단, 대항력 임차인 분석, 인수금액 산출, 세무/취득세 중과 검토, 목표 입찰가 역산
- **공적장부 및 규제 연동**: V-World 기반 공식 지목, 용도지역, 토지이음 규제구역(산업단지, 공공주택, 도시계획시설) 자동 진단
- **네이버 부동산 시세 및 GIS 지도**: 인근 상권, 역세권 거리, 실거래가 트렌드 및 지도 시각화
- **원클릭 전문가 보고서**: Word(`.docx`) 및 인쇄용 PDF 리포트 자동 다운로드

---

## 📂 폴더별 구조 및 상세 해설

프로젝트는 유지보수성과 배포 효율성을 극대화하기 위해 역할별로 명확히 분리·정리되어 있습니다.

```
ai-auction-experts/
├── 📁 backend/                # 백엔드 핵심 애플리케이션 및 분석 엔진
│   ├── app.py                 # FastAPI 메인 웹 서버 및 엔드포인트
│   ├── ai_analyzer.py         # Google Gemini AI 심층 권리분석 파이프라인
│   ├── doc_generator.py       # Word(.docx) 분석보고서 생성 모듈
│   ├── land_analyzer.py       # 토지 특성 및 규제 분석 로직
│   ├── naver_price_analyzer.py# 네이버 부동산 호가/실거래가 수집 및 분석
│   ├── vworld_land_service.py # 국토교통부 V-World 공적장부 실시간 연동
│   ├── sgis_service.py        # 통계청 SGIS 인구 및 통계 데이터 서비스
│   ├── pdf_analyzer.py        # 법원 서류 PDF 텍스트 추출 엔진
│   ├── crawler/               # 마이옥션, 온비드, 웹 검색 수집 스크래퍼
│   ├── parser/                # 경매 문서 및 지적 데이터 파서
│   ├── prompts/               # AI 심층 리포트 생성용 시스템 프롬프트
│   ├── scripts/               # 경매 DB 배치 및 공시지가 업데이트 스크립트
│   └── tests/                 # 백엔드 단위 테스트 및 검증 모듈
│
├── 📁 public/                 # 웹 프론트엔드 정적 파일
│   ├── index.html             # 메인 권리분석 대시보드 화면
│   ├── map.html               # 인터랙티브 GIS 경매 지도 화면
│   ├── analysis.html          # AI 추천 BEST 3 중첩 분석 화면
│   ├── script.js              # 프론트엔드 메인 UI 로직 및 비동기 API 통신
│   ├── style.css              # 모던 글래스모피즘 테마 스타일시트
│   └── dev_restriction.geojson# 규제 및 개발계획 공간 레이어
│
├── 📁 data/                   # 공시지가, 실거래가, 상권 등 대용량 데이터
│   ├── 네이버부동산/          # 네이버 부동산 크롤링 캐시 및 시세 데이터베이스
│   └── ...                    # SHP 지적/상권 원천 데이터
│
├── 📁 tools/                  # 개발/검증용 스크립트 및 아카이브 덤프
│   ├── 📁 test_scripts/       # 일회성 테스트, 디버깅, 데이터 검증 스크립트 (120+개)
│   └── 📁 archive_dumps/      # 개발 및 크롤링 테스트 과정에서 수집된 임시 덤프 데이터
│
├── 📁 scratch/                # 임시 작업용 스크래치 폴더 (Git 무시)
│
├── ⚙️ 실행 및 배포 스크립트
│   ├── start.bat              # 로컬 백엔드 서버 즉시 기동 (Windows)
│   ├── start_tunnel.bat       # Cloudflare Tunnel 외부 도메인 연결 기동
│   ├── deploy_to_aws.py       # AWS EC2 서버 원클릭 자동 배포 스크립트
│   ├── deploy_to_aws.bat      # 간편 AWS 배포 실행 배치파일
│   ├── update_data.bat        # 경매 최신 DB 업데이트 배치
│   ├── update_realprice.bat   # 실거래가 트렌드 업데이트 배치
│   └── sync_data_to_ec2.bat   # 대용량 DB 파일 원격 서버 동기화
│
└── 📄 시스템 설정 및 문서
    ├── .env                   # API 키 및 서버 설정 (Git 무시)
    ├── .gitignore             # 깃 형상관리 제외 목록 정의
    ├── requirements.txt       # 파이썬 의존성 패키지 명세
    ├── Dockerfile             # 컨테이너 빌드 파일
    ├── docker-compose.yml     # 멀티 컨테이너 설정
    ├── GEMINI.md              # AI 어시스턴트 권리분석 최우선 준수 규칙
    ├── CLAUDE.md              # 프로젝트 개발 표준 및 명령어 가이드
    └── AWS_DEPLOY_GUIDE.md    # EC2 배포 및 인프라 가이드
```

---

## 🚀 실행 가이드

### 1. 로컬 환경 실행
```bash
# 가상환경 활성화 및 패키지 설치
pip install -r requirements.txt

# 로컬 서버 실행 (포트 8001)
start.bat
# 또는
cd backend && python app.py
```
- 브라우저 접속: `http://localhost:8001`

### 2. AWS EC2 실서버 원클릭 배포
```bash
# 코드 및 UI 최신 패키지 초고속 배포 (권장)
python deploy_to_aws.py

# DB까지 함께 전체 동기화하여 배포할 경우
python deploy_to_aws.py --with-db
```
- 라이브 서비스 접속: [https://ai-auction-experts.cloud](https://ai-auction-experts.cloud)

### 3. 데이터베이스 갱신 배치
```bash
# 마이옥션 경매 데이터 최신화
update_data.bat

# 국토부 실거래가 시세 데이터 갱신
update_realprice.bat
```

---

## 🔄 Git 형상관리 및 롤백 가이드

본 저장소는 긴급 상황 시 안정된 과거 시점으로 신속히 롤백할 수 있도록 릴리즈 태그를 운영합니다.

### 📌 안정 릴리즈 기준점 (현재 기준)
- **Tag**: `v2.0-stable-20261022`
- **Branch**: `backup_apt_update` (Commit: `4fe36a0`)
- **내용**: AI 권리분석 파이프라인의 `import re` 오류 완전 해결, 10단계 심층 분석 마크다운 보고서 생성 검증 완료, AWS 라이브 서비스 정상 연동

### 롤백 명령어 (원클릭 복원)
```bash
# 안정 릴리즈 태그 시점으로 복원할 경우
git checkout v2.0-stable-20261022

# 최신 작업 브랜치로 복귀할 경우
git checkout backup_apt_update
```
