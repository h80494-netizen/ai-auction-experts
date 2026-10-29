# 🗄️ Database (`database/`) — 데이터베이스 스키마 · 마이그레이션 · 관리 도구

AI Auction Expert 2.0에서 사용하는 SQLite 공간·부동산 데이터베이스의 **전체 스키마 정의(`schema.sql`)**, **스키마 명세(`schemas/`)**, **데이터 적재 및 갱신 스크립트(`scripts/`)**를 통합 관리하는 디렉토리입니다.

> **런타임 경로 호환성 안내**: 실제 서버 구동 시 FastAPI 백엔드(`backend/app.py`)는 `backend/data/map_data.db` 및 `backend/data/small_business.db` 경로의 DB 파일을 직접 참조합니다. 프로그램 실행에 지장이 없도록 런타임 DB 경로는 그대로 유지됩니다.

---

## 📂 폴더 구조

```text
database/
├── README.md                           # 데이터베이스 아키텍처 및 테이블 명세서
├── schema.sql                          # 전체 테이블(34개) 및 인덱스(53개) DDL 스키마 정의
├── schemas/                            # 데이터 소스별 컬럼 및 스키마 요약 JSON
│   ├── auction_schema_summary.json     # 경·공매 원장 스키마 명세
│   └── gps_schema_summary.json         # 공간 좌표 및 주소 매핑 스키마 명세
└── scripts/                            # DB 구축·마이그레이션·업데이트 스크립트 모음
    ├── export_schema.py                # 운영 DB에서 최신 schema.sql 자동 추출 도구
    ├── import_auction_data.py          # 경·공매 엑셀 데이터 DB 적재
    ├── update_naver_db.py              # 네이버 부동산 매매/전월세 시세 DB 갱신
    ├── load_realprice_data.py          # 국토부 실거래가 CSV 격자(Grid) 집계 적재
    ├── update_realprice_trends.py      # 실거래가 변동률 및 신축/구축 시세 트렌드 계산
    ├── update_land_price.py            # 서울·경기·인천 공시지가 공간 매칭 업데이트
    ├── update_official_price.py        # 개별공시지가 정제 및 보정
    ├── build_small_biz_db.py           # 전국 소상공인 상권 DB(small_business.db) 빌드
    ├── process_redevelopment_and_zoning.py # 정비구역 및 용도지역 폴리곤 적재
    ├── import_gyeonggi_redevelopment.py    # 경기도 재개발·재건축 구역 적재
    ├── import_incheon_redevelopment.py     # 인천 재개발·재건축 구역 적재
    ├── load_deregulation_zones.py      # 규제완화구역 공간 데이터 적재
    ├── process_population_grid.py      # 500m 격자 유동/거주 인구 데이터 적재
    └── process_subway_lines.py         # 지하철 노선 및 역세권 좌표 적재
```

---

## 📊 핵심 데이터베이스 및 주요 테이블 현황

### 1. 통합 공간·경공매 DB (`backend/data/map_data.db` — 약 652 MB)

| 분류 | 테이블명 | 레코드 수 | 설명 |
| :--- | :--- | ---: | :--- |
| **경·공매 물건** | `auctions` | 31,210건 | 대법원 경매 및 온비드 공매 물건 정보, 감정가/최저가, 역세권 거리, 공시지가 |
| **네이버 시세** | `naver_real_estate` | 817,016건 | 네이버 부동산 매매·전세·월세 매물 호가, 면적, 층수, 연식, 좌표 |
| **실거래 격자** | `realprice_grids` | 77,961건 | 국토부 실거래가 기반 격자별 평당 매매가, 전세가율, 신축/구축 시세 |
| **도로망 데이터** | `road_cache_segments` | 379,067건 | OSM 기반 도로 폭·등급·좌표 세그먼트 캐시 |
| **도로 구간** | `road_segments` | 271,118건 | 정밀 도로 구간 BBox 및 지오메트리 |
| **대중교통** | `bus_stops` / `subways` | 64,347 / 1,349건 | 버스정류소 및 지하철역(개통/예정) 위치 정보 |
| **인구 격자** | `population_500m_grids` | 69,863건 | 500m 격자별 거주인구 및 직장인구 통계 |
| **용도/지구** | `zoning_polygons` / `district_units` | 42,993 / 11,261건 | 용도지역 및 지구단위계획구역 공간 폴리곤 |
| **도시계획** | `unexecuted_facilities` / `planning_roads` | 20,674 / 5,191건 | 장기미집행 도시계획시설 및 예정도로 폴리곤 |
| **정비사업** | `redevelopment_zones` | 3,078건 | 재개발·재건축·도심공공주택복합사업 구역 폴리곤 |
| **산업/학군** | `industrial_complexes` / `middle_schools` | 17,438 / 1,201건 | 산업단지 위치 및 중학교 특목고 진학률 데이터 |
| **운영/게시판** | `board_inquiries` / `approved_users` / `admin_notices` | - | 회원 승인, 문의 게시판, 공지사항 관리 테이블 |

### 2. 소상공인 상권 DB (`backend/data/small_business.db` — 약 980 MB)

| 분류 | 테이블명 | 레코드 수 | 설명 |
| :--- | :--- | ---: | :--- |
| **상권 점포** | `small_business` | 2,691,377건 | 전국 소상공인 업종(대·중·소분류), 상호, 지번/도로명 주소, 층·호수, 위경도 좌표 |

---

## 🔄 데이터베이스 정기 업데이트 방법

```bash
# 1. 경·공매 물건 및 공시지가 일괄 업데이트 (루트에서 실행)
update_data.bat

# 2. 국토부 실거래가 격자 시세 업데이트
update_realprice.bat

# 3. DB 스키마 변경 시 schema.sql 최신화
python database/scripts/export_schema.py
```
