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

## 🏗️ 3대 핵심 아키텍처 (프론트엔드 · 백엔드 · 데이터베이스)

프로젝트는 유지보수성과 직관적인 탐색을 위해 **프론트엔드(`public/`)**, **백엔드(`backend/`)**, **데이터베이스(`database/`)** 3대 영역으로 명확히 구분되어 있으며, 모든 기존 실행 스크립트와 100% 호환됩니다.

| 구분 | 디렉토리 | 핵심 역할 | 상세 문서 |
| :--- | :--- | :--- | :--- |
| 🎨 **Frontend** | [`public/`](./public/) | 대시보드(`index.html`), GIS 경매지도(`map.html`), 비교/이슈/관리자 UI 및 GeoJSON 공간 레이어 | [public/README.md](./public/README.md) |
| ⚙️ **Backend** | [`backend/`](./backend/) | FastAPI 웹 서버(`app.py`), Gemini AI 10단계 권리분석 엔진, 네이버 시세/토지 분석기, 법원·온비드 크롤러 | [backend/README.md](./backend/README.md) |
| 🗄️ **Database** | [`database/`](./database/) | 통합 SQLite 스키마(`schema.sql`), 테이블 명세(`schemas/`), DB 적재·마이그레이션 스크립트(`scripts/`) 및 런타임 DB(`backend/data/*.db`) | [database/README.md](./database/README.md) |

---

## 📂 전체 폴더 구조

```text
ai-auction-experts/
│
├── 🎨 public/                      # [프론트엔드] 웹 UI 및 GIS 공간 시각화 정적 파일
│   ├── README.md                   # 프론트엔드 상세 구조 안내
│   ├── index.html                  # 메인 AI 권리분석 대시보드 화면
│   ├── map.html                    # 인터랙티브 GIS 경매 지도 화면
│   ├── analysis.html               # AI 추천 BEST 3 중첩 분석 화면
│   ├── compare.html                # 다중 물건 비교 분석 화면
│   ├── issues.html                 # 개발호재·이슈 레이더 화면
│   ├── admin.html                  # 관리자 페이지 (공지/문의/승인 관리)
│   ├── script.js / style.css       # 프론트엔드 메인 로직 및 스타일시트
│   └── data/                       # 아파트 단지·학군·노후도·택지 등 GeoJSON 레이어
│
├── ⚙️ backend/                     # [백엔드] 핵심 API 서버, AI 분석 엔진 및 크롤러
│   ├── README.md                   # 백엔드 상세 아키텍처 안내
│   ├── app.py                      # FastAPI 메인 웹 서버 (Port: 8001)
│   ├── ai_analyzer.py              # Google Gemini AI 심층 권리분석 파이프라인
│   ├── naver_price_analyzer.py     # 네이버 부동산 매매/전월세 호가·실거래 시세 분석
│   ├── land_analyzer.py            # 토지 특성 및 공적 규제 분석 로직
│   ├── vworld_land_service.py      # 국토교통부 V-World 공적장부 실시간 연동
│   ├── sgis_service.py             # 통계청 SGIS 인구 및 통계 데이터 서비스
│   ├── doc_generator.py            # Word(.docx) 분석보고서 생성 모듈
│   ├── pdf_analyzer.py             # 법원 서류 PDF 텍스트 추출 엔진
│   ├── crawler/                    # 대법원 경매, 마이옥션, 온비드, 마당스 수집 스크래퍼
│   ├── parser/                     # 경매 문서 및 PDF 파서
│   ├── prompts/                    # AI 심층 리포트 생성용 시스템 프롬프트
│   ├── scripts/                    # 런타임 DB 배치 업데이트 스크립트
│   ├── tests/                      # 백엔드 단위 테스트 모듈
│   └── data/                       # 런타임 SQLite DB (map_data.db, small_business.db)
│
├── 🗄️ database/                    # [데이터베이스] 스키마, 명세서 및 DB 구축·갱신 도구
│   ├── README.md                   # DB 테이블 명세(34개 테이블) 및 운영 가이드
│   ├── schema.sql                  # 전체 SQLite 테이블 및 인덱스 DDL 스키마
│   ├── schemas/                    # 경공매/GPS 스키마 요약 JSON
│   └── scripts/                    # DB 빌드·마이그레이션·스키마 추출 스크립트 모음
│
├── 📁 data/                        # 공시지가(SHP), 실거래가, 네이버부동산 등 원천 데이터셋
├── 📁 tools/                       # 개발/검증용 테스트 스크립트 및 아카이브 백업 보관소
├── 📁 scratch/                     # 로컬 전용 임시 스크래치 폴더 (Git 추적 제외)
│
├── 🚀 실행 및 배포 스크립트
│   ├── start.bat                   # 로컬 백엔드 서버 및 대시보드 즉시 기동 (Windows)
│   ├── start_tunnel.bat            # Cloudflare Tunnel 외부 도메인 연결 기동
│   ├── deploy_to_aws.py            # AWS EC2 서버 원클릭 자동 배포 스크립트
│   ├── deploy_auction_update.py    # 경공매 업데이트 데이터 & DB 원클릭 배포
│   ├── deploy_naver_update.py      # 네이버 시세 DB & 분석 로직 원클릭 배포
│   ├── update_data.bat             # 경매 최신 DB 및 공시지가 업데이트 배치
│   └── update_realprice.bat        # 국토부 실거래가 트렌드 업데이트 배치
│
└── 📄 시스템 설정 및 규칙 문서
    ├── .gitattributes              # Git LFS 대용량 파일(*.db) 추적 설정
    ├── .gitignore                  # Git 형상관리 제외 목록 정의
    ├── requirements.txt            # 파이썬 의존성 패키지 명세
    ├── Dockerfile / docker-compose.yml # 컨테이너 빌드 및 배포 설정
    ├── GEMINI.md                   # AI 어시스턴트 권리분석 최우선 준수 규칙
    ├── CLAUDE.md                   # 6대 AI 에이전트 핵심 원칙 가이드
    └── AWS_DEPLOY_GUIDE.md         # AWS EC2 배포 및 인프라 운영 가이드
```

---

## 🚀 실행 가이드

### 1. 로컬 환경 실행
```bash
# 패키지 설치
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
# 경·공매 데이터 및 공시지가 최신화
update_data.bat

# 국토부 실거래가 시세 데이터 갱신
update_realprice.bat
```
