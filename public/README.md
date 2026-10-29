# 🎨 Frontend (`public/`) — 웹 프론트엔드 및 GIS 공간 시각화

AI Auction Expert 2.0의 사용자 인터페이스(UI) 및 인터랙티브 GIS 지도 레이어를 담당하는 프론트엔드 디렉토리입니다.  
FastAPI 서버(`backend/app.py`)에서 정적 파일 루트(`/`)로 직접 마운트되어 서비스됩니다.

---

## 📂 파일 구조

```text
public/
├── index.html                  # 메인 AI 권리분석 대시보드 및 사건번호 검색 화면
├── map.html                    # 인터랙티브 GIS 경·공매 지도 및 레이어 컨트롤러
├── analysis.html               # AI 추천 BEST 3 입지 중첩 분석 화면
├── compare.html                # 다중 경매 물건 비교 분석 화면
├── issues.html                 # 지역별 개발호재·이슈 레이더 화면
├── admin.html                  # 관리자 공지사항·문의게시판·회원 승인 관리 화면
├── script.js                   # 메인 대시보드 비동기 API 통신 및 리포트 렌더링 로직
├── style.css                   # 글래스모피즘(Glassmorphism) 다크/라이트 테마 스타일시트
├── eum_blueprint.png           # 토지이음 도면 분석 프리뷰 에셋
├── dev_promotion.geojson       # 개발진흥지구 공간 폴리곤 레이어
├── dev_restriction.geojson     # 개발제한구역(그린벨트) 공간 폴리곤 레이어
├── settlement.geojson          # 취락지구 공간 폴리곤 레이어
└── data/                       # 지도 오버레이용 상세 GeoJSON 데이터셋
    ├── apt_info.geojson                # 아파트 단지 포인트 및 세대수 정보
    ├── apt_info_500_polygons.geojson   # 500세대 이상 대단지 아파트 폴리곤
    ├── elite_school_dongs.geojson      # 특목고/명문학군 강세 행정동 경계
    ├── old_buildings.geojson           # 노후 건축물(35년 이상) 분포 데이터
    ├── old_buildings_ratio.geojson     # 구역별 노후도 비율 폴리곤
    ├── planned_roads_100m.geojson      # 예정도로 100m 버퍼 레이어
    ├── seoul_commercial.geojson        # 서울시 주요 상권 경계 레이어
    └── taekji.geojson                  # 택지개발지구 공간 레이어
```

---

## ⚡ 주요 특징
- **Canvas GPU 가속 & BBox 뷰포트 필터링**: 수만 건의 경·공매 마커와 수십만 건의 도로/용도지역 폴리곤을 지연 없이 렌더링합니다.
- **하트비트 Keep-Alive 연동**: `/api/ping` 주기적 호출 및 화면 복귀 시 자동 세션 깨우기(Wake-up)로 장시간 방치 후에도 프리징을 방지합니다.
