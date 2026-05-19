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
    return FileResponse(path=file_path, filename=f"{safe_case}_분석보고서.docx", media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

@app.get("/api/download/{case_number:path}")
async def download_report(case_number: str):
    safe_case = case_number.replace(" ", "_").replace("/", "_")
    file_path = os.path.join("downloads", f"{safe_case}_분석보고서.docx")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="보고서를 찾을 수 없습니다.")
    return FileResponse(path=file_path, filename=f"{safe_case}_분석보고서.docx", media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

@app.get("/api/download_ppt/{case_number:path}")
async def download_ppt(case_number: str):
    safe_case = case_number.replace(" ", "_").replace("/", "_")
    file_path = os.path.join("downloads", f"{safe_case}_브리핑자료.pptx")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PPTX 브리핑 자료를 찾을 수 없습니다.")
    return FileResponse(path=file_path, filename=f"{safe_case}_브리핑자료.pptx", media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation")

@app.get("/api/download_pdf/{case_number:path}")
async def download_pdf(case_number: str):
    safe_case = case_number.replace(" ", "_").replace("/", "_")
    file_path = os.path.join("downloads", f"{safe_case}_브리핑자료.pdf")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF 브리핑 자료를 찾을 수 없습니다.")
    return FileResponse(path=file_path, filename=f"{safe_case}_브리핑자료.pdf", media_type="application/pdf")

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
    regions: Optional[str] = None
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
    cases: Optional[str] = None
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

# 이미지 제공용 스태틱 라우트
test_images_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_images")
if os.path.exists(test_images_dir):
    app.mount("/test_images", StaticFiles(directory=test_images_dir), name="images")

public_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public")
if os.path.exists(public_dir):
    app.mount("/", StaticFiles(directory=public_dir, html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000)
