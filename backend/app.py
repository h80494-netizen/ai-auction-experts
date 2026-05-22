from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import sys
import asyncio
import io
import pandas as pd

# Windows 환경에서 Playwright와 Uvicorn 비동기 루프 충돌 방지
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# 로컬 스크래퍼 모듈 임포트
from crawler.myauction_scraper import scrape_myauction_case

import logging
logging.basicConfig(filename='server.log', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s: %(message)s')

app = FastAPI(title="AI Auction Analyst Backend")

@app.middleware("http")
async def log_requests(request, call_next):
    logging.info(f"Incoming request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logging.info(f"Response status: {response.status_code}")
        return response
    except Exception as e:
        logging.error(f"Request failed with exception: {str(e)}", exc_info=True)
        raise

# CORS 설정 (프론트엔드 HTML에서 호출 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 보안을 위해 향후 프론트엔드 도메인으로 제한 필요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from typing import Optional

class AnalyzeRequest(BaseModel):
    case_number: str
    address_hint: Optional[str] = ""
    property_type: Optional[str] = "주택"
    house_count: Optional[int] = 0
    investor_type: Optional[str] = "개인"
    investment_duration: Optional[str] = "6개월"
    target_return_rate: Optional[float] = 20.0
    repair_condition: Optional[str] = "수리불필요"
    is_regulated_area: Optional[bool] = False
    madangs_url: Optional[str] = ""

class SearchRequest(BaseModel):
    case_number: str

class PasswordRequest(BaseModel):
    password: str

@app.post("/api/verify")
async def verify_password(request: PasswordRequest):
    if request.password == "1234":
        return {"status": "success"}
    else:
        return {"status": "error"}


@app.post("/api/search_cases")
async def search_cases(request: SearchRequest):
    """
    사건번호로 검색 가능한 주소(물건) 목록을 반환합니다.
    """
    case_number = request.case_number
    print(f"[{case_number}] 사건번호 검색 목록 요청")
    
    from fastapi.concurrency import run_in_threadpool
    
    def _run_search(c_num):
        import asyncio
        if "-" in c_num:
            from crawler.madangs_scraper import search_madangs_list
            return asyncio.run(search_madangs_list(c_num))
        else:
            from crawler.myauction_scraper import search_myauction_list
            return asyncio.run(search_myauction_list(c_num))
        
    result = await run_in_threadpool(_run_search, case_number)
    if result.get("success"):
        return {"status": "success", "data": result.get("items", [])}
    else:
        return {"status": "error", "message": result.get("error", "검색 실패")}

import uuid

analysis_tasks = {}

async def _background_analyze(task_id: str, request: AnalyzeRequest):
    case_number = request.case_number
    address_hint = request.address_hint
    print(f"[{case_number}] 백그라운드 분석 시작 (task_id: {task_id})")
    
    from fastapi.concurrency import run_in_threadpool
    
    def _run_scraper(c_num, a_hint):
        import asyncio
        if "-" in c_num:
            from crawler.madangs_scraper import scrape_madangs_case
            return asyncio.run(scrape_madangs_case(c_num, a_hint))
        else:
            from crawler.myauction_scraper import scrape_myauction_case
            return asyncio.run(scrape_myauction_case(c_num, a_hint))
        
    try:
        result = await run_in_threadpool(_run_scraper, case_number, address_hint)
        
        if request.madangs_url and "-" not in case_number:
            def _run_madangs(c_num, m_url):
                import asyncio
                from crawler.madangs_scraper import scrape_madangs_images
                asyncio.run(scrape_madangs_images(c_num, m_url))
            try:
                print("마당스 URL이 감지되어 사진 강제 교체를 시도합니다.")
                await run_in_threadpool(_run_madangs, case_number, request.madangs_url)
            except Exception as e:
                print(f"마당스 사진 교체 실패: {e}")
                
        if result["success"]:
            result["data"]["property_type"] = request.property_type
            result["data"]["house_count"] = request.house_count
            result["data"]["investor_type"] = request.investor_type
            result["data"]["investment_duration"] = request.investment_duration
            result["data"]["target_return_rate"] = request.target_return_rate
            result["data"]["repair_condition"] = request.repair_condition
            result["data"]["is_regulated_area"] = request.is_regulated_area
            
            result["data"]["appraised_value"] = result["data"].get("appraised_value", "3800000000") 
            result["data"]["minimum_value"] = result["data"].get("minimum_value", "3000000000") 
            result["data"]["address"] = result["data"].get("address", "경기도 성남시 수정구 신흥동 2465-7 신흥역하늘채랜더스원")
            result["data"]["risks"] = result["data"].get("risks", [])

            try:
                from ai_analyzer import generate_deep_research
                import re
                deep_research_text = await run_in_threadpool(generate_deep_research, result["data"])
                result["data"]["analysis"] = deep_research_text
                
                ai_sise = re.search(r"예상시세:\s*([0-9,]+)", deep_research_text)
                ai_insu = re.search(r"예상인수금액:\s*([0-9,]+)", deep_research_text)
                ai_target = re.search(r"목표입찰가:\s*([0-9,]+)", deep_research_text)
                
                if ai_sise and ai_target:
                    result["data"]["ai_sise"] = int(ai_sise.group(1).replace(",", "")) * 10000
                    result["data"]["ai_insu"] = int(ai_insu.group(1).replace(",", "")) * 10000 if ai_insu else 0
                    result["data"]["ai_target"] = int(ai_target.group(1).replace(",", "")) * 10000
                    
            except Exception as e:
                result["data"]["analysis"] = f"AI 심층 분석 중 오류 발생: {str(e)}"

            try:
                from doc_generator import generate_analysis_doc
                doc_path = generate_analysis_doc(result["data"])
                doc_msg = f"보고서 생성 완료: {doc_path} (구글독스 업로드 가능)"
            except Exception as e:
                doc_msg = f"보고서 생성 실패: {str(e)}"
                
            analysis_tasks[task_id] = {
                "status": "success",
                "message": f"데이터 수집 및 문서 생성 완료. AI 에이전트 분석 중... ({doc_msg})",
                "data": result["data"]
            }
        else:
            analysis_tasks[task_id] = {
                "status": "error",
                "message": f"크롤링 실패: {result.get('error')}"
            }
    except Exception as e:
        analysis_tasks[task_id] = {
            "status": "error",
            "message": f"분석 중 예외 발생: {str(e)}"
        }

@app.post("/api/analyze")
async def analyze_case(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """
    프론트엔드에서 사건번호를 받아 백엔드 분석 파이프라인을 비동기로 시작합니다.
    """
    task_id = str(uuid.uuid4())
    analysis_tasks[task_id] = {"status": "processing"}
    background_tasks.add_task(_background_analyze, task_id, request)
    
    return {
        "status": "processing",
        "task_id": task_id,
        "message": "분석이 시작되었습니다. 결과를 기다리는 중입니다..."
    }

@app.get("/api/analyze/status/{task_id}")
async def get_analyze_status(task_id: str):
    task_info = analysis_tasks.get(task_id)
    if not task_info:
        return {"status": "error", "message": "유효하지 않은 Task ID입니다."}
    return task_info

import os
from pydantic import BaseModel

class DownloadRequest(BaseModel):
    markdown: str

@app.post("/api/download/{case_number:path}")
async def download_report_post(case_number: str, req: DownloadRequest):
    safe_case = case_number.replace(" ", "_").replace("/", "_")
    file_path = os.path.join("downloads", f"{safe_case}_분석보고서.docx")
    
    try:
        from doc_generator import generate_analysis_doc_from_markdown
        generate_analysis_doc_from_markdown(case_number, req.markdown, "downloads")
    except Exception as e:
        print("Word 문서 재생성 실패:", e)
        
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="보고서를 찾을 수 없습니다.")
    
    import urllib.parse
    encoded_filename = urllib.parse.quote(f"{safe_case}_분석보고서.docx")
    headers = {"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
    return FileResponse(path=file_path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers=headers)

@app.get("/api/download/{case_number:path}")
async def download_report(case_number: str):
    safe_case = case_number.replace(" ", "_").replace("/", "_")
    file_path = os.path.join("downloads", f"{safe_case}_분석보고서.docx")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="보고서를 찾을 수 없습니다.")
    
    import urllib.parse
    encoded_filename = urllib.parse.quote(f"{safe_case}_분석보고서.docx")
    headers = {"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
    return FileResponse(path=file_path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers=headers)

@app.get("/api/download_ppt/{case_number:path}")
async def download_ppt(case_number: str):
    safe_case = case_number.replace(" ", "_").replace("/", "_")
    file_path = os.path.join("downloads", f"{safe_case}_브리핑자료.pptx")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PPTX 브리핑 자료를 찾을 수 없습니다.")
    
    import urllib.parse
    encoded_filename = urllib.parse.quote(f"{safe_case}_브리핑자료.pptx")
    headers = {"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
    return FileResponse(path=file_path, media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation", headers=headers)

@app.get("/api/download_pdf/{case_number:path}")
async def download_pdf(case_number: str):
    safe_case = case_number.replace(" ", "_").replace("/", "_")
    file_path = os.path.join("downloads", f"{safe_case}_브리핑자료.pdf")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF 브리핑 자료를 찾을 수 없습니다.")
    
    import urllib.parse
    encoded_filename = urllib.parse.quote(f"{safe_case}_브리핑자료.pdf")
    headers = {"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
    return FileResponse(path=file_path, media_type="application/pdf", headers=headers)

downloads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "downloads")


@app.get("/api/images/{case_number:path}")
async def get_images(case_number: str):
    safe_case = case_number.replace(" ", "_").replace("/", "_")
    dir_path = os.path.join(downloads_dir, safe_case)
    if not os.path.exists(dir_path):
        dir_path = os.path.join(downloads_dir, case_number)
        
    images = []
    if os.path.exists(dir_path):
        for f in os.listdir(dir_path):
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                images.append(f)
    
    # Sort them so photo_01 comes before photo_02
    images.sort()
    
    # If no images, return empty list or maybe the default ones
    if not images:
        return {"status": "success", "images": []}
        
    return {"status": "success", "images": images}

@app.get("/api/download_image/{case_number:path}/{filename}")
async def download_image(case_number: str, filename: str):
    safe_case = case_number.replace(" ", "_").replace("/", "_")
    file_path = os.path.join(downloads_dir, safe_case, filename)
    if not os.path.exists(file_path):
        file_path = os.path.join(downloads_dir, case_number, filename)
    if not os.path.exists(file_path):
        test_images_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_images")
        file_path = os.path.join(test_images_dir, "thumb_0.png")
    return FileResponse(path=file_path)


@app.get("/api/download_photo/{case_number:path}")
async def download_photo(case_number: str):
    safe_case = case_number.replace(" ", "_").replace("/", "_")
    file_path = os.path.join(downloads_dir, safe_case, "photo.jpg")
    if not os.path.exists(file_path):
        file_path = os.path.join(downloads_dir, case_number, "photo.jpg")
    if not os.path.exists(file_path):
        test_images_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_images")
        file_path = os.path.join(test_images_dir, "thumb_0.png")
    return FileResponse(path=file_path)

@app.get("/api/download_map/{case_number:path}")
async def download_map(case_number: str):
    safe_case = case_number.replace(" ", "_").replace("/", "_")
    file_path = os.path.join(downloads_dir, safe_case, "map.jpg")
    if not os.path.exists(file_path):
        file_path = os.path.join(downloads_dir, case_number, "map.jpg")
    if not os.path.exists(file_path):
        return await download_photo(case_number)
    return FileResponse(path=file_path)

@app.get("/api/download_structure/{case_number:path}")
async def download_structure(case_number: str):
    safe_case = case_number.replace(" ", "_").replace("/", "_")
    file_path = os.path.join(downloads_dir, safe_case, "structure.jpg")
    if not os.path.exists(file_path):
        file_path = os.path.join(downloads_dir, case_number, "structure.jpg")
    if not os.path.exists(file_path):
        return await download_photo(case_number)
    return FileResponse(path=file_path)

from fastapi.staticfiles import StaticFiles
from typing import Optional
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'map_data.db')

@app.get("/api/map/pois")
def get_map_pois(
    min_lat: Optional[float] = None,
    max_lat: Optional[float] = None,
    min_lng: Optional[float] = None,
    max_lng: Optional[float] = None,
    regions: Optional[str] = None
):
    if not os.path.exists(DB_PATH):
        return {"status": "error", "message": "DB not found"}
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query_condition = ""
    params = []
    if min_lat and max_lat and min_lng and max_lng:
        query_condition = " WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?"
        params = [min_lat, max_lat, min_lng, max_lng]

    region_condition = ""
    region_params = []
    if regions:
        region_list = regions.split(',')
        region_clauses = " OR ".join(["address LIKE ?" for _ in region_list])
        region_condition = f" AND ({region_clauses})" if query_condition else f" WHERE ({region_clauses})"
        region_params = [f"{r}%" for r in region_list]

    # Combine query_condition and region_condition for tables with 'address' column
    combined_condition = ""
    combined_params = []
    if query_condition and region_condition:
        combined_condition = query_condition + region_condition.replace("WHERE", "AND", 1)
        combined_params = params + region_params
    elif query_condition:
        combined_condition = query_condition
        combined_params = params
    elif region_condition:
        combined_condition = region_condition
        combined_params = region_params

    cursor.execute(f"SELECT line, name, address, lat, lng FROM subways{combined_condition} LIMIT 500", combined_params)
    subways = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute(f"SELECT name, address, lat, lng FROM universities{combined_condition} LIMIT 500", combined_params)
    universities = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute(f"SELECT name, address, lat, lng, special_hs_rate FROM middle_schools{combined_condition} LIMIT 500", combined_params)
    middle_schools = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute(f"SELECT name, lat, lng FROM industrial_complexes{query_condition} LIMIT 500", params)
    industrial_complexes = [dict(row) for row in cursor.fetchall()]

    bus_stops = []
    # Only fetch bus stops if bounding box is provided (to prevent crashing with 200k items)
    if min_lat and max_lat and min_lng and max_lng:
        cursor.execute('''
            SELECT name, lat, lng FROM bus_stops 
            WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ? LIMIT 500
        ''', (min_lat, max_lat, min_lng, max_lng))
        bus_stops = [dict(row) for row in cursor.fetchall()]
        
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='commercial_areas'")
    has_commercial = cursor.fetchone()
    commercial_areas = []
    
    # commercial_areas are only in Seoul
    is_seoul_selected = True
    if regions:
        region_list = regions.split(',')
        if not any(r.startswith("서울") for r in region_list):
            is_seoul_selected = False

    if has_commercial and is_seoul_selected:
        cursor.execute(f"SELECT name, category, lat, lng, population FROM commercial_areas{query_condition} LIMIT 500", params)
        commercial_areas = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "status": "success",
        "data": {
            "subways": subways,
            "universities": universities,
            "middle_schools": middle_schools,
            "industrial_complexes": industrial_complexes,
            "bus_stops": bus_stops,
            "commercial_areas": commercial_areas
        }
    }

@app.get("/api/map/hagwon_polygons")
def get_map_hagwon_polygons():
    if not os.path.exists(DB_PATH):
        return {"status": "error", "message": "DB not found"}
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='hagwon_polygons'")
    if not cursor.fetchone():
        conn.close()
        return {"status": "success", "data": []}
        
    cursor.execute("SELECT id, count, coordinates_json FROM hagwon_polygons")
    polygons = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {"status": "success", "data": polygons}

@app.get("/api/map/district_units")
def get_district_units(
    min_lat: Optional[float] = None,
    max_lat: Optional[float] = None,
    min_lng: Optional[float] = None,
    max_lng: Optional[float] = None
):
    if not os.path.exists(DB_PATH):
        return {"status": "error", "message": "DB not found"}
        
    if not (min_lat and max_lat and min_lng and max_lng):
        return {"status": "success", "data": []}
        
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='district_units'")
    if not cursor.fetchone():
        conn.close()
        return {"status": "success", "data": []}
        
    query = '''
        SELECT id, name, geojson FROM district_units
        WHERE max_lat >= ? AND min_lat <= ? 
          AND max_lng >= ? AND min_lng <= ?
        LIMIT 500
    '''
    cursor.execute(query, (min_lat, max_lat, min_lng, max_lng))
    data = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return {"status": "success", "data": data}

@app.get("/api/map/subway_lines")
def get_map_subway_lines():
    if not os.path.exists(DB_PATH):
        return {"status": "error", "message": "DB not found"}
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='subway_lines'")
    if not cursor.fetchone():
        conn.close()
        return {"status": "success", "data": []}
        
    cursor.execute("SELECT id, line, coordinates_json FROM subway_lines")
    lines = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {"status": "success", "data": lines}

@app.get("/api/map/auctions")
def get_map_auctions(
    property_types: Optional[str] = None, # comma separated
    min_rate: Optional[float] = 0,
    sale_type: Optional[str] = None, # '경매', '공매', '전체'
    min_lat: Optional[float] = None,
    max_lat: Optional[float] = None,
    min_lng: Optional[float] = None,
    max_lng: Optional[float] = None,
    min_area: Optional[float] = None,
    max_area: Optional[float] = None,
    subway_dist_max: Optional[float] = None,
    univ_dist_max: Optional[float] = None,
    ind_dist_max: Optional[float] = None,
    req_elite_school: Optional[bool] = False,
    min_households: Optional[int] = None,
    regions: Optional[str] = None,
    special_rights: Optional[str] = None,
    land_prices: Optional[str] = None
):
    if not os.path.exists(DB_PATH):
        return {"status": "error", "message": "DB not found"}
        
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auctions'")
    if not cursor.fetchone():
        conn.close()
        return {"status": "success", "data": []}

    query = "SELECT * FROM auctions WHERE 1=1"
    params = []
    
    if min_lat and max_lat and min_lng and max_lng:
        query += " AND lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?"
        params.extend([min_lat, max_lat, min_lng, max_lng])
        
    if regions:
        region_list = regions.split(',')
        region_clauses = " OR ".join(["address LIKE ?" for _ in region_list])
        query += f" AND ({region_clauses})"
        params.extend([f"{r}%" for r in region_list])
        
    if sale_type and sale_type != '전체':
        query += " AND sale_type = ?"
        params.append(sale_type)
        
    if min_rate:
        query += " AND min_bid_rate <= ?"
        params.append(min_rate)
        
    if property_types:
        types_list = property_types.split(',')
        type_clauses = []
        for t in types_list:
            if t == '아파트':
                type_clauses.append("property_type = '아파트'")
            elif t == '다세대':
                type_clauses.append("property_type = '다세대'")
            elif t == '오피스텔':
                type_clauses.append("property_type = '오피스텔'")
            elif t == '단독':
                type_clauses.append("property_type = '단독'")
            elif t == '지산':
                type_clauses.append("property_type = '지산'")
            elif t == '집합':
                type_clauses.append("property_type = '집합'")
            elif t == '일반':
                type_clauses.append("property_type = '일반'")
            elif t == '토지':
                type_clauses.append("property_type = '토지'")
            elif t == '공장':
                type_clauses.append("property_type = '공장'")
            elif t == '기타':
                type_clauses.append("(property_type NOT IN ('아파트', '다세대', '오피스텔', '단독', '지산', '집합', '일반', '토지', '공장'))")
            else:
                type_clauses.append("property_type = ?")
                params.append(t)
        
        if type_clauses:
            query += f" AND ({' OR '.join(type_clauses)})"

    if min_area is not None:
        query += " AND area_size >= ?"
        params.append(min_area)
    if max_area is not None:
        query += " AND area_size <= ?"
        params.append(max_area)
    if subway_dist_max is not None:
        query += " AND subway_dist > 0 AND subway_dist <= ?"
        params.append(subway_dist_max)
    if univ_dist_max is not None:
        query += " AND univ_dist > 0 AND univ_dist <= ?"
        params.append(univ_dist_max)
    if ind_dist_max is not None:
        query += " AND ind_dist > 0 AND ind_dist <= ?"
        params.append(ind_dist_max)
    if req_elite_school:
        query += " AND (elite_school LIKE 'Yes%' OR elite_school LIKE 'yes%')"
    if min_households is not None:
        query += " AND households >= ?"
        params.append(min_households)
    if special_rights:
        rights_list = special_rights.split(',')
        rights_clauses = []
        for r in rights_list:
            if r == '기타':
                rights_clauses.append("special_notes != ''")
            elif r == '법정지상권':
                rights_clauses.append("(special_notes LIKE ? OR special_notes LIKE ? OR special_notes LIKE ?)")
                params.extend([f"%{r}%", "%토지만매각%", "%건물만매각%"])
            elif r == '지분경매':
                rights_clauses.append("(special_notes LIKE ? OR special_notes LIKE ? OR special_notes LIKE ?)")
                params.extend([f"%{r}%", "%지분%", "%공유%"])
            else:
                rights_clauses.append("special_notes LIKE ?")
                params.append(f"%{r}%")
        if rights_clauses:
            query += f" AND ({' OR '.join(rights_clauses)})"
    if land_prices:
        lp_list = land_prices.split(',')
        lp_clauses = []
        for lp in lp_list:
            if lp == '1억이하':
                lp_clauses.append("(official_land_price > 0 AND official_land_price <= 100000000)")
            elif lp == '1억~2억':
                lp_clauses.append("(official_land_price > 100000000 AND official_land_price <= 200000000)")
            elif lp == '2억~3억':
                lp_clauses.append("(official_land_price > 200000000 AND official_land_price <= 300000000)")
        if lp_clauses:
            query += f" AND ({' OR '.join(lp_clauses)})"

    query += " LIMIT 1500"
    cursor.execute(query, params)
    auctions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {"status": "success", "data": auctions}

@app.get("/api/map/auctions/export")
def export_map_auctions(
    min_lat: Optional[float] = None,
    max_lat: Optional[float] = None,
    min_lng: Optional[float] = None,
    max_lng: Optional[float] = None,
    sale_type: Optional[str] = None,
    property_types: Optional[str] = None,
    min_rate: Optional[float] = None,
    min_area: Optional[float] = None,
    max_area: Optional[float] = None,
    subway_dist_max: Optional[float] = None,
    univ_dist_max: Optional[float] = None,
    ind_dist_max: Optional[float] = None,
    req_elite_school: Optional[bool] = None,
    min_households: Optional[int] = None,
    regions: Optional[str] = None,
    cases: Optional[str] = None,
    special_rights: Optional[str] = None,
    land_prices: Optional[str] = None
):
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=404, detail="DB not found")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auctions'")
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Table not found")

    query = "SELECT case_no as 사건번호, sale_type as 구분, property_type as 종류, address as 주소, appraisal_price as 감정가, min_price as 최저가, min_bid_rate as 최저가율, area_size as 건물평수, land_size as 대지평수, min_price_per_pyeong as 평당최저가격, subway_dist as 지하철거리, univ_dist as 대학교거리, ind_dist as 산업단지거리, elite_school as 학군, households as 세대수 FROM auctions WHERE 1=1"
    params = []

    if cases:
        case_list = cases.split(',')
        placeholders = ','.join(['?'] * len(case_list))
        query += f" AND case_no IN ({placeholders})"
        params.extend(case_list)
    else:
        if min_lat and max_lat and min_lng and max_lng:
            query += " AND lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?"
            params.extend([min_lat, max_lat, min_lng, max_lng])
        
    if regions:
        region_list = regions.split(',')
        region_clauses = " OR ".join(["address LIKE ?" for _ in region_list])
        query += f" AND ({region_clauses})"
        params.extend([f"{r}%" for r in region_list])
        
    if sale_type and sale_type != '전체':
        query += " AND sale_type = ?"
        params.append(sale_type)
        
    if min_rate:
        query += " AND min_bid_rate <= ?"
        params.append(min_rate)
        
    if property_types:
        types_list = property_types.split(',')
        type_clauses = []
        for t in types_list:
            if t == '아파트':
                type_clauses.append("property_type = '아파트'")
            elif t == '다세대':
                type_clauses.append("property_type = '다세대'")
            elif t == '오피스텔':
                type_clauses.append("property_type = '오피스텔'")
            elif t == '단독':
                type_clauses.append("property_type = '단독'")
            elif t == '지산':
                type_clauses.append("property_type = '지산'")
            elif t == '집합':
                type_clauses.append("property_type = '집합'")
            elif t == '일반':
                type_clauses.append("property_type = '일반'")
            elif t == '토지':
                type_clauses.append("property_type = '토지'")
            elif t == '공장':
                type_clauses.append("property_type = '공장'")
            elif t == '기타':
                type_clauses.append("(property_type NOT IN ('아파트', '다세대', '오피스텔', '단독', '지산', '집합', '일반', '토지', '공장'))")
            else:
                type_clauses.append("property_type = ?")
                params.append(t)
        
        if type_clauses:
            query += f" AND ({' OR '.join(type_clauses)})"

    if min_area is not None:
        query += " AND area_size >= ?"
        params.append(min_area)
    if max_area is not None:
        query += " AND area_size <= ?"
        params.append(max_area)
    if subway_dist_max is not None:
        query += " AND subway_dist > 0 AND subway_dist <= ?"
        params.append(subway_dist_max)
    if univ_dist_max is not None:
        query += " AND univ_dist > 0 AND univ_dist <= ?"
        params.append(univ_dist_max)
    if ind_dist_max is not None:
        query += " AND ind_dist > 0 AND ind_dist <= ?"
        params.append(ind_dist_max)
    if req_elite_school:
        query += " AND (elite_school LIKE 'Yes%' OR elite_school LIKE 'yes%')"
    if min_households is not None:
        query += " AND households >= ?"
        params.append(min_households)
    if special_rights:
        rights_list = special_rights.split(',')
        rights_clauses = []
        for r in rights_list:
            if r == '기타':
                rights_clauses.append("special_notes != ''")
            elif r == '법정지상권':
                rights_clauses.append("(special_notes LIKE ? OR special_notes LIKE ? OR special_notes LIKE ?)")
                params.extend([f"%{r}%", "%토지만매각%", "%건물만매각%"])
            elif r == '지분경매':
                rights_clauses.append("(special_notes LIKE ? OR special_notes LIKE ? OR special_notes LIKE ?)")
                params.extend([f"%{r}%", "%지분%", "%공유%"])
            else:
                rights_clauses.append("special_notes LIKE ?")
                params.append(f"%{r}%")
        if rights_clauses:
            query += f" AND ({' OR '.join(rights_clauses)})"
    if land_prices:
        lp_list = land_prices.split(',')
        lp_clauses = []
        for lp in lp_list:
            if lp == '1억이하':
                lp_clauses.append("(official_land_price > 0 AND official_land_price <= 100000000)")
            elif lp == '1억~2억':
                lp_clauses.append("(official_land_price > 100000000 AND official_land_price <= 200000000)")
            elif lp == '2억~3억':
                lp_clauses.append("(official_land_price > 200000000 AND official_land_price <= 300000000)")
        if lp_clauses:
            query += f" AND ({' OR '.join(lp_clauses)})"

    cursor.execute(query, params)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    df = pd.DataFrame(rows)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='경공매_추출결과')
    
    output.seek(0)
    
    headers = {
        'Content-Disposition': 'attachment; filename="auction_export.xlsx"'
    }
    
    return StreamingResponse(output, headers=headers, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.get("/api/map/population_heatmap")
def get_population_heatmap(min_lat: float, max_lat: float, min_lng: float, max_lng: float):
    db_path = os.path.join(os.path.dirname(__file__), '../data/map_data.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='population_grids'")
    if not cursor.fetchone():
        conn.close()
        return {"status": "error", "message": "Population data not loaded yet."}

    query = '''
        SELECT lat, lng, avg_population FROM population_grids
        WHERE lat BETWEEN ? AND ? 
          AND lng BETWEEN ? AND ?
    '''
    cursor.execute(query, (min_lat, max_lat, min_lng, max_lng))
    grids = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {"status": "success", "data": grids}

@app.get("/api/map/demographics")
def get_map_demographics(lat: float, lng: float):
    """
    물건지 클릭 시 반경 1km 내 배후수요 분석 데이터를 반환합니다.
    SGIS OpenAPI를 연동하며, 실패 시 로컬 공간 추정 엔진(Fallback)이 작동합니다.
    지하철역과의 거리 및 역세권 판정도 함께 제공합니다.
    """
    import math
    import random
    from sgis_service import sgis_service
    
    # 1. 지하철역 정보 수색 (1km 이내 전체 및 가장 가까운 역)
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'map_data.db')
    if not os.path.exists(db_path):
        db_path = os.path.join(os.path.dirname(__file__), '../data/map_data.db')
        
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 하버사인 거리 계산 헬퍼 함수
    def haversine_distance(lat1, lon1, lat2, lon2):
        R = 6371000  # 지구 반경 (m)
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    # 바운딩 박스를 이용한 고속 1차 필터링 (~0.015도, 약 1.5km)
    lat_delta = 0.015
    lng_delta = 0.018
    
    cursor.execute('''
        SELECT name, line, address, lat, lng FROM subways
        WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?
    ''', (lat - lat_delta, lat + lat_delta, lng - lng_delta, lng + lng_delta))
    
    subway_rows = cursor.fetchall()
    
    subways_in_1km = []
    closest_subway = None
    min_dist = float('inf')
    
    for row in subway_rows:
        s = dict(row)
        dist = haversine_distance(lat, lng, s['lat'], s['lng'])
        s['distance'] = round(dist)
        if dist <= 1000:
            subways_in_1km.append(s)
            if dist < min_dist:
                min_dist = dist
                closest_subway = s
                
    # 역세권 판정
    station_grade = "비역세권"
    if closest_subway:
        if closest_subway['distance'] <= 500:
            station_grade = "초역세권"
        else:
            station_grade = "역세권"
            
    # 2. SGIS OpenAPI 연동 시도
    demographics = None
    try:
        demographics = sgis_service.fetch_demographics_500(lat, lng)
    except Exception as e:
        logging.error(f"SGIS Real-time fetch error: {e}")
        
    # 3. 로컬 공간 엔진을 이용한 Fallback 연산 (SGIS 실패 또는 키 미등록 시)
    if not demographics:
        logging.info("SGIS API unavailable. Running Local Spatial Estimation Engine...")
        
        # 3.1. 주거/유동인구 추정 (500m 이내 격자 생활인구의 합산)
        cursor.execute('''
            SELECT avg_population, lat, lng FROM population_grids
            WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?
        ''', (lat - lat_delta, lat + lat_delta, lng - lng_delta, lng + lng_delta))
        grid_rows = cursor.fetchall()
        
        total_pop = 0
        grid_count = 0
        for row in grid_rows:
            g = dict(row)
            dist = haversine_distance(lat, lng, g['lat'], g['lng'])
            if dist <= 500:
                total_pop += g['avg_population']
                grid_count += 1
                
        # 서울 외 지역이거나 그리드가 없는 경우 기본 추정치 보정
        if total_pop == 0:
            # 경기도/인천 등 외곽 지역의 기본값 제공
            total_pop = 22000 + int(random.Random(int(lat*1000)).random() * 10000)
            
        # 세대수 계산 (평균 가구원 수 2.2명 기준 + 변동)
        total_households = int(total_pop / 2.25)
        
        # 3.2. 일자리 및 업체수 추정 (상권 데이터를 활용)
        cursor.execute('''
            SELECT name, population, category, lat, lng FROM commercial_areas
            WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?
        ''', (lat - lat_delta, lat + lat_delta, lng - lng_delta, lng + lng_delta))
        comm_rows = cursor.fetchall()
        
        total_comm_pop = 0
        comm_count = 0
        for row in comm_rows:
            c = dict(row)
            dist = haversine_distance(lat, lng, c['lat'], c['lng'])
            if dist <= 500:
                total_comm_pop += c['population']
                comm_count += 1
                
        # 업체수 및 직장인구(종사자수) 스케일링 계산 (500m 반경에 맞게 현실적으로 보정)
        if total_comm_pop > 0:
            companies = comm_count * 4 + int(total_comm_pop * 0.0002) + 15
            workplace_pop = int(total_comm_pop * 0.004) + comm_count * 8 + 120
        else:
            # 오피스가 부재한 순수 주거지 기본값
            seed_val = int(lat*1000 + lng*1000)
            rng = random.Random(seed_val)
            companies = 10 + rng.randint(5, 20)
            workplace_pop = 60 + rng.randint(20, 100)
            
        # 3.3. 연령층 분포 생성 (위도/경도 기반 결정론적 난수로 현실적인 배분)
        seed_val = int(lat*10000 + lng*10000)
        rng = random.Random(seed_val)
        
        w_under20 = rng.uniform(0.12, 0.16)
        w_20s = rng.uniform(0.13, 0.17)
        w_30s = rng.uniform(0.16, 0.20)
        w_40s = rng.uniform(0.19, 0.23)
        w_55s = rng.uniform(0.15, 0.18)
        w_sum = w_under20 + w_20s + w_30s + w_40s + w_55s
        
        # 정규화
        w_under20 /= w_sum
        w_20s /= w_sum
        w_30s /= w_sum
        w_40s /= w_sum
        w_55s /= w_sum
        w_60s = 1.0 - (w_under20 + w_20s + w_30s + w_40s + w_55s)
        
        age_groups = {
            "under_20s": int(total_pop * w_under20),
            "twenties": int(total_pop * w_20s),
            "thirties": int(total_pop * w_30s),
            "forties": int(total_pop * w_40s),
            "fifties": int(total_pop * w_55s),
            "sixties_plus": int(total_pop * w_60s)
        }
        
        demographics = {
            "source": "Local Spatial Engine",
            "residential_population": int(total_pop),
            "households": int(total_households),
            "companies": int(companies),
            "workplace_population": int(workplace_pop),
            "age_distribution": age_groups
        }
        
    # 4. 250m 이내 유동인구 산출 (주거/직장인구 비율 및 격자 데이터를 바탕으로 시간대/주중주말 세분화)
    cursor.execute('''
        SELECT avg_population, lat, lng FROM population_grids
        WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?
    ''', (lat - 0.003, lat + 0.003, lng - 0.004, lng + 0.004))
    grid_rows_250 = cursor.fetchall()
    
    total_pop_250 = 0
    for row in grid_rows_250:
        g = dict(row)
        dist = haversine_distance(lat, lng, g['lat'], g['lng'])
        if dist <= 250:
            total_pop_250 += g['avg_population']
            
    res_pop = demographics["residential_population"]
    wrk_pop = demographics["workplace_population"]
    
    # 250m 이내 생활인구 보정
    if total_pop_250 == 0:
        total_pop_250 = int(res_pop * 0.25) + 800
        
    office_ratio = wrk_pop / (res_pop + wrk_pop + 100)
    
    if office_ratio > 0.4:
        weekday_pop = int(total_pop_250 * 1.35)
        weekend_pop = int(total_pop_250 * 0.45)
        lunch_pop = int(weekday_pop * 0.38)
        dinner_pop = int(weekday_pop * 0.32)
    else:
        weekday_pop = int(total_pop_250 * 0.85)
        weekend_pop = int(total_pop_250 * 1.25)
        lunch_pop = int(total_pop_250 * 0.22)
        dinner_pop = int(total_pop_250 * 0.28)
        
    floating_population_250 = {
        "weekday": weekday_pop,
        "weekend": weekend_pop,
        "lunch": lunch_pop,
        "dinner": dinner_pop,
        "total": total_pop_250
    }
    
    demographics["floating_population_250"] = floating_population_250

    # 5. 지하철역명 중복 제거 및 노선 그룹화
    grouped_subways = {}
    for s in subways_in_1km:
        base_name = s['name']
        if base_name.endswith('역'):
            base_name = base_name[:-1]
            
        if base_name not in grouped_subways:
            grouped_subways[base_name] = {
                'name': base_name,
                'lines': [],
                'distance': s['distance'],
                'lat': s['lat'],
                'lng': s['lng'],
                'address': s['address']
            }
        else:
            if s['distance'] < grouped_subways[base_name]['distance']:
                grouped_subways[base_name]['distance'] = s['distance']
                grouped_subways[base_name]['lat'] = s['lat']
                grouped_subways[base_name]['lng'] = s['lng']
                
        line_clean = s['line']
        if line_clean.startswith('서울') and len(line_clean) > 2 and line_clean[2].isdigit():
            line_clean = line_clean[2:]
        if line_clean not in grouped_subways[base_name]['lines']:
            grouped_subways[base_name]['lines'].append(line_clean)

    subways_in_1km_grouped = []
    for base_name, info in grouped_subways.items():
        subways_in_1km_grouped.append({
            'name': base_name,  # '역'을 제외하고 보냄 (프론트에서 `${s.name}역`으로 포맷팅하므로 중복 방지)
            'line': ", ".join(info['lines']),
            'distance': info['distance'],
            'lat': info['lat'],
            'lng': info['lng'],
            'address': info['address']
        })
        
    if closest_subway:
        closest_base_name = closest_subway['name']
        if closest_base_name.endswith('역'):
            closest_base_name = closest_base_name[:-1]
        if closest_base_name in grouped_subways:
            closest_grouped = grouped_subways[closest_base_name]
            closest_subway = {
                'name': closest_grouped['name'],
                'line': ", ".join(closest_grouped['lines']),
                'distance': closest_grouped['distance'],
                'lat': closest_grouped['lat'],
                'lng': closest_grouped['lng'],
                'address': closest_grouped['address']
            }

    conn.close()
    
    # 6. 종합 및 배후수요 종합 분석 평가
    res_pop = demographics["residential_population"]
    wrk_pop = demographics["workplace_population"]
    
    # 배후수요 유형 평가
    if wrk_pop > res_pop * 0.7:
        demand_assessment = "오피스 상업 중심지 (유동/직장인 유입 최상)"
        assessment_detail = "주거 밀도보다 일자리가 고밀도로 밀집한 핵심 경제 활동 구역입니다. 직장인 배후수요가 매우 강해 직산이나 상가 임대수요가 극대화되는 지역입니다."
        recom_biz = "커피전문점, 테이크아웃 샐러드/샌드위치 전문점, 직장인 대상 캐주얼 한식/일식당, 피트니스/필라테스 센터, 퓨전 요리 주점"
        recom_desc = "직장인들의 점심 시간 소비 및 퇴근 후 여가 소비가 집중되는 지역으로, 고회전율 식음료 업종 및 스트레스 해소형 운동시설을 적극 추천합니다."
    elif res_pop > 150000:
        demand_assessment = "주거 초고밀도 구역 (배후수요 안정성 극대)"
        assessment_detail = "가구 및 주택 밀집도가 대단히 높은 초대형 아파트 단지 및 주택가입니다. 생필품, 소매점, 학군 중심의 실수요 배후가 탄탄하며 낙찰 시 매매/전세 회전율이 우수합니다."
        recom_biz = "프랜차이즈 베이커리, 입시/보습 학원, 대형 편의점 및 무인 아이스크림점, 세탁/수선 전문점, 소아과/치과 의원"
        recom_desc = "탄탄한 고정 가족 단위 배후 수요를 바탕으로 생활 밀착형 소매점, 교육 서비스, 가족 단위 외식 및 필수 의료 서비스 업종이 매우 안정적입니다."
    else:
        demand_assessment = "배후수요 안정지대 (주거밀집 구역)"
        assessment_detail = "주거 배후수요와 근린 생활 수요가 조화롭게 분포된 지역입니다. 지하철 접근성에 따라 가치가 민감하게 반응하므로 지하철 인프라 연동 분석을 필히 활용하세요."
        recom_biz = "근린 생활 밀착형 편의점, 베이커리 카페, 무인 빨래방, 반찬 전문점, 헤어숍/미용실"
        recom_desc = "안정적인 주거 배후를 바탕으로 일상 소비 빈도가 높은 무인 점포 및 1인 가구/가족 소단위 밀착형 서비스가 지속적이고 안정적인 매출을 보장합니다."

    # 유동인구 250m 특징 추가
    floating_detail = f"\n\n[입지 평가 특징 - 250m 이내 유동인구]\n- 주중 일평균 유동인구: 약 {weekday_pop:,}명 | 주말 일평균 유동인구: 약 {weekend_pop:,}명\n- 시간대별 분포: 점심(11~14시) 약 {lunch_pop:,}명 | 저녁(18~21시) 약 {dinner_pop:,}명"
    assessment_detail += floating_detail

    # 추천업종 추가
    recommended_detail = f"\n\n[입지 기반 추천 업종]\n- 권장 업종: {recom_biz}\n- 추천 사유: {recom_desc}"
    assessment_detail += recommended_detail

    return {
        "status": "success",
        "subway_proximity": {
            "grade": station_grade,
            "closest_station": closest_subway,
            "all_stations_in_1km": sorted(subways_in_1km_grouped, key=lambda x: x['distance'])
        },
        "demographics": demographics,
        "assessment": {
            "class": demand_assessment,
            "detail": assessment_detail,
            "recom_biz": recom_biz,
            "recom_desc": recom_desc
        }
    }

@app.get("/api/map/grid_demographics")
def get_grid_demographics(
    min_lat: float, max_lat: float, min_lng: float, max_lng: float,
    type: str = "residential",  # "residential" | "workplace" | "floating"
    regions: Optional[str] = "서울"
):
    """
    지도 화면(BBox) 영역 내 격자형 인구 데이터를 조회합니다.
    서울은 기존 DB에서, 경기/인천은 고성능 공간 추정 엔진(Fallback)으로 실시간 생성하여 독립 로컬 정규화를 지원합니다.
    """
    import math
    import random
    
    # 250m 격자 위경도 증가 스텝 기본값 선언
    lat_step = 0.00225
    lng_step = 0.0028
    
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'map_data.db')
    if not os.path.exists(db_path):
        db_path = os.path.join(os.path.dirname(__file__), '../data/map_data.db')
        
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    selected_regions = regions.split(',') if regions else ["서울"]
    show_seoul = any("서울" in r for r in selected_regions)
    show_gyeonggi = any("경기" in r for r in selected_regions)
    show_incheon = any("인천" in r for r in selected_regions)
    
    grids = []
    
    # 1. 서울 그리드 로딩 (기존 DB 활용)
    if show_seoul:
        seoul_grids = []
        if type == "workplace":
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='commercial_areas'")
            if cursor.fetchone():
                query = '''
                    SELECT lat, lng, population as avg_population, name as grid_id FROM commercial_areas
                    WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?
                    LIMIT 1000
                '''
                cursor.execute(query, (min_lat, max_lat, min_lng, max_lng))
                seoul_grids = [dict(row) for row in cursor.fetchall()]
        elif type == "residential":
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='population_grids'")
            if cursor.fetchone():
                query = '''
                    SELECT lat, lng, (avg_population * 0.85) as avg_population, grid_id FROM population_grids
                    WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?
                    LIMIT 1000
                '''
                cursor.execute(query, (min_lat, max_lat, min_lng, max_lng))
                seoul_grids = [dict(row) for row in cursor.fetchall()]
        else:  # "floating"
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='population_grids'")
            if cursor.fetchone():
                query = '''
                    SELECT lat, lng, avg_population, grid_id FROM population_grids
                    WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?
                    LIMIT 1000
                '''
                cursor.execute(query, (min_lat, max_lat, min_lng, max_lng))
                seoul_grids = [dict(row) for row in cursor.fetchall()]
                
        # 서울 그리드 태깅
        for g in seoul_grids:
            g["region"] = "seoul"
            grids.append(g)

    # 2. 경기 & 인천 그리드 초고속 실시간 합성 (POI 배치 로드 + 메모리 연산)
    if (show_gyeonggi or show_incheon) and (max_lat - min_lat < 0.50) and (max_lng - min_lng < 0.55):
        # Bbox 외곽 1km 패딩을 주어 경계지역 버스정류장/지하철 등이 짤리지 않게 처리
        pad_lat = 0.009
        pad_lng = 0.011
        
        # 단 1번의 배치 DB 쿼리로 Bbox 안의 모든 관련 POI 수집 (메모리 로딩)
        # 지하철역 배치 로드
        cursor.execute('''
            SELECT name, address, lat, lng FROM subways
            WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?
        ''', (min_lat - pad_lat, max_lat + pad_lat, min_lng - pad_lng, max_lng + pad_lng))
        subways = [dict(r) for r in cursor.fetchall()]
        
        # 학교 배치 로드
        cursor.execute('''
            SELECT name, address, lat, lng FROM middle_schools
            WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?
        ''', (min_lat - pad_lat, max_lat + pad_lat, min_lng - pad_lng, max_lng + pad_lng))
        schools = [dict(r) for r in cursor.fetchall()]
        
        cursor.execute('''
            SELECT name, address, lat, lng FROM universities
            WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?
        ''', (min_lat - pad_lat, max_lat + pad_lat, min_lng - pad_lng, max_lng + pad_lng))
        schools.extend([dict(r) for r in cursor.fetchall()])
        
        # 경공매 물건지 배치 로드 (물건지 근방은 고밀도 주거지로 설정)
        cursor.execute('''
            SELECT address, lat, lng, property_type FROM auctions
            WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?
        ''', (min_lat - pad_lat, max_lat + pad_lat, min_lng - pad_lng, max_lng + pad_lng))
        auctions = [dict(r) for r in cursor.fetchall()]
        
        # 버스정류장 배치 로드 (지연 방지를 위해 최대 300개 제한)
        cursor.execute('''
            SELECT name, lat, lng FROM bus_stops
            WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?
            LIMIT 300
        ''', (min_lat - pad_lat, max_lat + pad_lat, min_lng - pad_lng, max_lng + pad_lng))
        bus_stops = [dict(r) for r in cursor.fetchall()]
        
        # 초고속 메모리 Euclidean Approximation 함수
        # 위도 37.5도 기준: 위도 1도=111,000m, 경도 1도=88,000m
        def fast_dist(lat1, lng1, lat2, lng2):
            dy = (lat1 - lat2) * 111000.0
            dx = (lng1 - lng2) * 88000.0
            return math.sqrt(dx*dx + dy*dy)

        # BBox 내에 250m 간격으로 중심점 그리드 매핑
        grid_id_counter = 0
        
        # 루프를 돌기 전 루프 횟수가 1200개를 초과하면 가벼운 스텝으로 자동 스케일 조절해 속도 강제 방어
        while True:
            lat_count = int((max_lat - min_lat) / lat_step) + 1
            lng_count = int((max_lng - min_lng) / lng_step) + 1
            if lat_count * lng_count > 1200:
                lat_step *= 1.5
                lng_step *= 1.5
            else:
                break
            
        curr_lat = min_lat
        while curr_lat <= max_lat:
            curr_lng = min_lng
            while curr_lng <= max_lng:
                # 1. 주변 가장 가까운 지하철역 또는 학교의 주소를 조회해 경기/인천 여부 판정
                nearest_poi = None
                min_poi_d = float('inf')
                
                # 지하철역에서 검색
                for s in subways:
                    d = fast_dist(curr_lat, curr_lng, s["lat"], s["lng"])
                    if d < min_poi_d:
                        min_poi_d = d
                        nearest_poi = s
                        
                # 학교에서 검색
                for sch in schools:
                    d = fast_dist(curr_lat, curr_lng, sch["lat"], sch["lng"])
                    if d < min_poi_d:
                        min_poi_d = d
                        nearest_poi = sch
                        
                # 경매 물건지에서 검색
                for auc in auctions:
                    d = fast_dist(curr_lat, curr_lng, auc["lat"], auc["lng"])
                    if d < min_poi_d:
                        min_poi_d = d
                        nearest_poi = auc

                # 소속 지역 판단
                grid_region = None
                if nearest_poi:
                    address_str = nearest_poi.get("address", "")
                    if "인천" in address_str or "인천광역시" in address_str:
                        grid_region = "incheon"
                    elif "경기" in address_str or "경기도" in address_str:
                        grid_region = "gyeonggi"
                    elif "서울" in address_str or "서울특별시" in address_str:
                        grid_region = "seoul"  # 서울로 판정되면 서울 고정 격자와 중복되므로 제외
                else:
                    # 인접 POI가 전혀 없으면 순수 외곽지역 좌표로 단순 추정
                    if curr_lng < 126.734:
                        grid_region = "incheon"
                    else:
                        grid_region = "gyeonggi"

                # 경기 혹은 인천 그리드이면서, 유저가 클릭해 활성화된 지역인 경우에만 연산 수행
                if grid_region and grid_region != "seoul":
                    is_active = (grid_region == "incheon" and show_incheon) or (grid_region == "gyeonggi" and show_gyeonggi)
                    if is_active:
                        # 2. 고성능 인메모리 근접 가중치 계산 (Distance-Decay Weight)
                        score = 0.0
                        
                        # 가중치 튜닝 변수
                        w_sub, w_bus, w_auc, w_sch = 1.0, 1.0, 1.0, 1.0
                        if type == "residential":
                            w_sub, w_bus, w_auc, w_sch = 0.8, 0.9, 1.3, 1.2
                        elif type == "workplace":
                            w_sub, w_bus, w_auc, w_sch = 1.2, 1.1, 1.1, 0.6
                        else: # floating
                            w_sub, w_bus, w_auc, w_sch = 1.4, 1.3, 0.8, 0.7
                            
                        # 지하철 기여도
                        for s in subways:
                            d = fast_dist(curr_lat, curr_lng, s["lat"], s["lng"])
                            if d <= 500:
                                score += 12000 * (1 - d / 500.0) * w_sub
                                
                        # 버스정류장 기여도
                        for b in bus_stops:
                            d = fast_dist(curr_lat, curr_lng, b["lat"], b["lng"])
                            if d <= 200:
                                score += 2500 * (1 - d / 200.0) * w_bus
                                
                        # 경공매 물건지 (거주/건물 밀도) 기여도
                        for auc in auctions:
                            d = fast_dist(curr_lat, curr_lng, auc["lat"], auc["lng"])
                            if d <= 300:
                                # 상업용 지산/집합/일반 등 종류에 따라 직장/주거 인구 매칭 보정
                                p_type = auc.get("property_type", "주택")
                                multi = 1.0
                                if type == "workplace" and p_type in ["지산", "집합", "공장", "일반"]:
                                    multi = 1.5
                                elif type == "residential" and p_type in ["아파트", "다세대", "오피스텔", "단독"]:
                                    multi = 1.5
                                score += 5000 * (1 - d / 300.0) * w_auc * multi
                                
                        # 학교 기여도
                        for sch in schools:
                            d = fast_dist(curr_lat, curr_lng, sch["lat"], sch["lng"])
                            if d <= 300:
                                score += 3500 * (1 - d / 300.0) * w_sch

                        # 3. 사실적 분포 연산 및 결과 저장
                        # 숲이나 외딴 비주거 무인 지역(score < 2000)은 그리드를 아예 그리지 않아 속도 향상
                        if score >= 2000:
                            # 결정론적 난수를 시드로 적용하여 격자에 미세한 사실감 넘치는 노이즈 생성
                            random_seed = int((curr_lat * 10000 + curr_lng * 10000) % 100000)
                            rng = random.Random(random_seed)
                            noise = rng.uniform(0.85, 1.15)
                            
                            avg_pop = int(score * 0.95 * noise)
                            
                            grid_id = f"synth_{grid_region}_{grid_id_counter}"
                            grids.append({
                                "lat": round(curr_lat, 6),
                                "lng": round(curr_lng, 6),
                                "avg_population": avg_pop,
                                "grid_id": grid_id,
                                "region": grid_region
                            })
                            grid_id_counter += 1
                            
                curr_lng += lng_step
            curr_lat += lat_step
            
    conn.close()
    return {
        "status": "success", 
        "data": grids, 
        "lat_step": lat_step, 
        "lng_step": lng_step
    }

@app.get("/api/map/road_flows")
def get_road_flows(
    min_lat: float, max_lat: float, min_lng: float, max_lng: float
):
    """
    지하철역을 중심으로 한 procedural 보행자 방사형 네트워크(Radial Walkability Network)를 생성합니다.
    OSM Overpass API 의존성 및 격자 형태의 시각화를 배제하고, 역 중심 반경 250m 영역 내에서
    8개의 구불구불한 스포크(spokes)와 2개의 concentric octagon 링을 로컬 연산(<5ms)으로 생성합니다.
    거리 d에 따라 지수적 감쇄 모델 (e^-2.5*(d/250))을 적용하여 사실적인 도보 동선 유동량을 나타냅니다.
    """
    import math
    import random
    import sqlite3
    import os

    # 1. BBox 영역 내 지하철역 정보 수집
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'map_data.db')
    if not os.path.exists(db_path):
        db_path = os.path.join(os.path.dirname(__file__), '../data/map_data.db')
    if not os.path.exists(db_path):
        db_path = 'map_data.db'

    subways = []
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT name, lat, lng FROM subways
                WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?
                LIMIT 50
            ''', (min_lat, max_lat, min_lng, max_lng))
            subways = [dict(r) for r in cursor.fetchall()]
            conn.close()
        except Exception as e:
            print("Failed to query subways from db:", e)

    # 2. 지하철역이 없는 외곽 또는 특수 지역의 경우 예외 방어용 가상 중심점 생성
    if not subways:
        mid_lat = (min_lat + max_lat) / 2.0
        mid_lng = (min_lng + max_lng) / 2.0
        subways.append({
            "name": "임시 역세권 중심",
            "lat": mid_lat,
            "lng": mid_lng
        })

    features = []

    # 한국 위도(37.5도) 기준 거리 변환 계수
    METERS_PER_LAT = 111000.0
    METERS_PER_LNG = 88000.0

    # 결정론적 난수를 생성하여 매 호출 시 지도에 고정된 형상이 나타나도록 시드 고정
    for s in subways:
        s_name = s["name"]
        lat_center = s["lat"]
        lng_center = s["lng"]
        
        # 지하철역 명칭별 고정 시드 확보
        seed_val = abs(hash(s_name)) % 1000000
        rng = random.Random(seed_val)
        
        # 반경 250m 설정
        R_max = 250.0 
        
        # 5m 단위 wiggling 크기 (경도/위도 단위로 변환)
        wiggle_lat_limit = 5.0 / METERS_PER_LAT
        wiggle_lng_limit = 5.0 / METERS_PER_LNG
        
        # 8개 방향 (0, 45, 90, 135, 180, 225, 270, 315 도)
        angles = [i * (2 * math.pi / 8) for i in range(8)]
        
        # ----------------------------------------------------
        # A. 8개 Spoke 생성 (중심에서 외곽 250m로 뻗어 나가는 선분)
        # 각 Spoke를 3개의 세그먼트로 나누어 wiggling 적용
        # ----------------------------------------------------
        spoke_points_by_angle = {} # 링(ring) 생성에 사용하기 위해 각 spoke의 분할점들을 저장
        
        for i, theta in enumerate(angles):
            # 분할 지점 비율 (0.0: 중심, 0.4: 내부, 0.8: 외부, 1.0: 최외곽)
            ratios = [0.0, 0.4, 0.8, 1.0]
            points = []
            
            # 중심점 (첫번째 점)은 정확히 역 위치 고정
            points.append([lng_center, lat_center])
            
            for r_ratio in ratios[1:]:
                # 미터 거리
                dist_m = r_ratio * R_max
                
                # 기본 좌표
                d_lat = (dist_m * math.sin(theta)) / METERS_PER_LAT
                d_lng = (dist_m * math.cos(theta)) / METERS_PER_LNG
                
                p_lat = lat_center + d_lat
                p_lng = lng_center + d_lng
                
                # wiggling (구불구불한 5m 흔들림 적용, 시작점 제외)
                p_lat += rng.uniform(-wiggle_lat_limit, wiggle_lat_limit)
                p_lng += rng.uniform(-wiggle_lng_limit, wiggle_lng_limit)
                
                points.append([p_lng, p_lat])
            
            spoke_points_by_angle[i] = points
            
            # 각 Spoke 상의 개별 세그먼트 생성하여 가중치 개별 반영
            for seg_idx in range(len(points) - 1):
                pt1 = points[seg_idx]
                pt2 = points[seg_idx+1]
                
                # 세그먼트 중간점 거리 계산
                r_ratio_mid = (ratios[seg_idx] + ratios[seg_idx+1]) / 2.0
                dist_mid = r_ratio_mid * R_max
                
                # 지수 감쇄 가중치 e^(-2.5 * d/250)
                decay = math.exp(-2.5 * (dist_mid / R_max))
                
                # 유동량 스케일링 (중심 3500명에서 지수 감쇄)
                intensity = decay
                avg_flow = int(intensity * 3500 + rng.randint(100, 300))
                
                # 5단계 유동 유형 결정
                if intensity >= 0.8:
                    flow_type = "매우 높음"
                elif intensity >= 0.5:
                    flow_type = "높음"
                elif intensity >= 0.3:
                    flow_type = "중간"
                elif intensity >= 0.1:
                    flow_type = "낮음"
                else:
                    flow_type = "매우 낮음"
                    
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [pt1, pt2]
                    },
                    "properties": {
                        "road_name": f"{s_name}역 {int(theta*180/math.pi)}도 도보길",
                        "road_class": "residential",
                        "flow_intensity": round(intensity, 2),
                        "avg_hourly_flow": avg_flow,
                        "flow_type": flow_type
                    }
                })

        # ----------------------------------------------------
        # B. 2개 Concentric Octagon Rings 생성
        # 각 Spoke의 중간 분할점들을 순환 연결하여 8각형 고리를 만듦
        # Ring 1: ratios[1] (0.4 비율, 약 100m 지점)
        # Ring 2: ratios[2] (0.8 비율, 약 200m 지점)
        # ----------------------------------------------------
        for ring_idx, ratio_val in [(1, 0.4), (2, 0.8)]:
            ring_dist = ratio_val * R_max
            decay = math.exp(-2.5 * (ring_dist / R_max))
            
            intensity = decay
            avg_flow = int(intensity * 3500 + rng.randint(100, 300))
            
            if intensity >= 0.8:
                flow_type = "매우 높음"
            elif intensity >= 0.5:
                flow_type = "높음"
            elif intensity >= 0.3:
                flow_type = "중간"
            elif intensity >= 0.1:
                flow_type = "낮음"
            else:
                flow_type = "매우 낮음"

            # 8개 스포크 상의 점들을 차례로 연결
            for i in range(8):
                pt_curr = spoke_points_by_angle[i][ring_idx]
                pt_next = spoke_points_by_angle[(i + 1) % 8][ring_idx]
                
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [pt_curr, pt_next]
                    },
                    "properties": {
                        "road_name": f"{s_name}역 {int(ring_dist)}m 보행순환선",
                        "road_class": "pedestrian",
                        "flow_intensity": round(intensity, 2),
                        "avg_hourly_flow": avg_flow,
                        "flow_type": flow_type
                    }
                })

    geojson_result = {
        "type": "FeatureCollection",
        "features": features
    }
    
    return {"status": "success", "data": geojson_result}

# 이미지 제공용 스태틱 라우트
test_images_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_images")
if os.path.exists(test_images_dir):
    app.mount("/test_images", StaticFiles(directory=test_images_dir), name="images")

public_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public")
if os.path.exists(public_dir):
    app.mount("/", StaticFiles(directory=public_dir, html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000)
