# ⚙️ Backend (`backend/`) — FastAPI 서버 · AI 권리분석 · 크롤링 엔진

AI Auction Expert 2.0의 백엔드 API 서버, 6대 에이전트 기반 Gemini AI 권리분석 파이프라인, 공적장부(V-World/SGIS) 연동 및 경·공매 크롤러를 담당하는 디렉토리입니다.

---

## 📂 폴더 및 파일 구조

```text
backend/
├── app.py                              # FastAPI 메인 웹 서버 (포트 8001, REST API & 정적 파일 서빙)
├── ai_analyzer.py                      # Google Gemini AI 10단계 심층 권리분석 파이프라인
├── naver_price_analyzer.py             # 네이버 부동산 매매/전월세 호가 및 실거래가 비교 분석 엔진
├── land_analyzer.py                    # 토지 특성, 접도 조건, 용도지역 및 보상/규제 분석 모듈
├── vworld_land_service.py              # 국토교통부 V-World 공적장부 API 실시간 연동
├── sgis_service.py                     # 통계청 SGIS 인구·가구·상권 통계 API 연동
├── sbiz_api.py                         # 소상공인시장진흥공단 상권 정보 연동 모듈
├── pdf_analyzer.py                     # 대법원 감정평가서·매각물건명세서 PDF 텍스트 추출기
├── doc_generator.py                    # Word(.docx) 전문가용 권리분석 보고서 생성기
├── notebooklm_ppt.py                   # 프레젠테이션 브리핑 생성 보조 모듈
│
├── crawler/                            # 경·공매 및 부동산 데이터 수집 스크래퍼
│   ├── court_scraper.py                # 대법원 법원경매 정보 수집기
│   ├── myauction_scraper.py            # 마이옥션 경매 사건 상세 스크래퍼
│   ├── onbid_scraper.py / onbid_api.py # 온비드(KAMCO) 공매 물건 수집기
│   ├── madangs_scraper.py              # 마당스 경매 데이터 연동 스크래퍼
│   └── issue_scanner.py                # 지역별 부동산 개발호재/이슈 자동 스캐너
│
├── parser/                             # 문서 파싱 모듈
│   └── pdf_extractor.py                # 법원 문건 PDF 파서
│
├── prompts/                            # AI 에이전트 시스템 프롬프트
│   └── deep_research_prompt.md         # 10단계 심층 권리분석 및 수익률 역산 프롬프트
│
├── scripts/                            # 데이터베이스 배치 적재 및 공간 데이터 가공 스크립트
│   ├── import_auction_data.py          # 최신 경·공매 엑셀 원장 DB 임포트
│   ├── update_land_price.py            # 공시지가 공간 매칭 및 DB 업데이트
│   └── ...                             # 도로망, 학군, 지하철, 상권 폴리곤 처리 스크립트
│
├── data/                               # 런타임 SQLite 데이터베이스 저장소
│   ├── map_data.db                     # 메인 통합 공간/경공매/시세 DB
│   ├── small_business.db               # 소상공인 상가 업종 DB
│   └── visitors.json                   # 방문자 통계 데이터
│
└── tests/                              # 백엔드 단위 테스트 및 스크래퍼 검증 스크립트
```

---

## 🚀 서버 기동 방법

```bash
# 프로젝트 루트에서 실행 시
start.bat

# 직접 실행 시
cd backend
python app.py
```
- 기본 접속 주소: `http://localhost:8001`
