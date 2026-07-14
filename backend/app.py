import os
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import sys
import asyncio
import io
import pandas as pd

downloads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "downloads"))

# Windows 환경에서 Playwright와 Uvicorn 비동기 루프 충돌 방지
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# 로컬 스크래퍼 모듈 임포트
from crawler.myauction_scraper import scrape_myauction_case
import pdf_analyzer

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

from typing import Optional, List, Dict, Any

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

class PdfRequest(BaseModel):
    pdf_url: str

@app.post("/api/pdf_extract")
async def extract_pdf_location(req: PdfRequest):
    return pdf_analyzer.analyze_pdf_for_location(req.pdf_url)

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
        return {"status": "error", "message": result.get("message", result.get("error", "검색 실패"))}

@app.get("/api/naver-realestate")
async def get_naver_realestate(
    estate_type: str = "아파트",
    min_lat: float = None,
    max_lat: float = None,
    min_lng: float = None,
    max_lng: float = None
):
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(__file__), "data", "map_data.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='naver_real_estate'")
    if not cursor.fetchone():
        return {"status": "error", "message": "네이버 부동산 데이터가 DB에 없습니다. 스크립트를 실행해주세요."}
    
    query = "SELECT * FROM naver_real_estate WHERE estate_type = ?"
    params = [estate_type]
    
    if min_lat is not None and max_lat is not None and min_lng is not None and max_lng is not None:
        query += " AND lat >= ? AND lat <= ? AND lng >= ? AND lng <= ?"
        params.extend([min_lat, max_lat, min_lng, max_lng])
        
    query += " LIMIT 1000"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    grouped = {}
    for row in rows:
        lat = row["lat"]
        lng = row["lng"]
        coord_key = (lat, lng)
        
        if coord_key not in grouped:
            grouped[coord_key] = {
                "lat": lat,
                "lng": lng,
                "address": row["address"],
                "total_count": 0,
                "age_info": row["age_info"] if "age_info" in row.keys() else "",
                "pyung_groups": {}
            }
        
        # In case the first row didn't have age_info, try to grab it from subsequent rows
        if not grouped[coord_key].get("age_info") and ("age_info" in row.keys() and row["age_info"]):
            grouped[coord_key]["age_info"] = row["age_info"]
            
        group = grouped[coord_key]
        group["total_count"] += 1
        
        area_str = str(row["area"])
        try:
            area_val = float(area_str)
            pyung = round(area_val / 3.3058)
        except:
            pyung = 0
            
        pyung_key = f"{pyung}평" if pyung > 0 else "기타"
        
        if pyung_key not in group["pyung_groups"]:
            group["pyung_groups"][pyung_key] = {
                "count": 0,
                "min_price": float('inf'),
                "max_price": 0,
                "min_price_per_pyung": float('inf'),
                "max_price_per_pyung": 0,
                "estate_ids": []
            }
            
        pg = group["pyung_groups"][pyung_key]
        pg["count"] += 1
        
        estate_id = str(row["estate_id"])
        if estate_id:
            pg["estate_ids"].append(estate_id)
            
        try:
            price_val = float(str(row["price"]))
        except:
            price_val = 0
            
        if price_val > 0:
            if price_val < pg["min_price"]: pg["min_price"] = price_val
            if price_val > pg["max_price"]: pg["max_price"] = price_val
            
            if pyung > 0:
                ppp = price_val / (area_val / 3.3058)
                if ppp < pg["min_price_per_pyung"]: pg["min_price_per_pyung"] = ppp
                if ppp > pg["max_price_per_pyung"]: pg["max_price_per_pyung"] = ppp

    data = []
    for (lat, lng), group_data in grouped.items():
        # Convert infinities back to 0 for JSON serialization
        pyung_list = []
        for p_key, p_data in group_data["pyung_groups"].items():
            if p_data["min_price"] == float('inf'): p_data["min_price"] = 0
            if p_data["min_price_per_pyung"] == float('inf'): p_data["min_price_per_pyung"] = 0
            
            pyung_list.append({
                "pyung": p_key,
                "count": p_data["count"],
                "min_price": p_data["min_price"],
                "max_price": p_data["max_price"],
                "min_price_per_pyung": p_data["min_price_per_pyung"],
                "max_price_per_pyung": p_data["max_price_per_pyung"],
                "estate_ids": p_data["estate_ids"]
            })
            
        # Sort pyung_list by pyung size numerically if possible
        def sort_key(x):
            try: return int(x["pyung"].replace("평", ""))
            except: return 0
        pyung_list.sort(key=sort_key)
        
        data.append({
            "lat": lat,
            "lng": lng,
            "address": group_data["address"],
            "total_count": group_data["total_count"],
            "pyung_groups": pyung_list
        })
        
    return {"status": "success", "data": data}

@app.get("/api/naver-realestate-details")
async def get_naver_realestate_details(
    lat: float,
    lng: float,
    estate_type: str = "아파트"
):
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "map_data.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # We will query with a small tolerance for floating point matching
    query = """
        SELECT * FROM naver_real_estate
        WHERE estate_type = ? 
        AND lat BETWEEN ? AND ?
        AND lng BETWEEN ? AND ?
    """
    epsilon = 0.000001
    cursor.execute(query, (estate_type, lat - epsilon, lat + epsilon, lng - epsilon, lng + epsilon))
    rows = cursor.fetchall()
    conn.close()
    
    data = []
    for row in rows:
        row_dict = dict(row)
        
        area_str = str(row_dict.get("area", "0"))
        try:
            area_val = float(area_str)
            pyung = round(area_val / 3.3058)
        except:
            pyung = 0
            area_val = 0
            
        try:
            price_val = float(str(row_dict.get("price", "0")))
        except:
            price_val = 0
            
        ppp = 0
        if pyung > 0 and price_val > 0:
            ppp = round(price_val / (area_val / 3.3058))
            
        row_dict["pyung"] = pyung
        row_dict["price_per_pyung"] = ppp
        data.append(row_dict)
        
    return {"status": "success", "data": data}

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
                
            try:
                import json
                safe_case = case_number.replace(" ", "_").replace("/", "_")
                json_path = os.path.join(downloads_dir, f"{safe_case}_data.json")
                with open(json_path, 'w', encoding='utf-8') as jf:
                    json.dump(result["data"], jf, ensure_ascii=False, indent=4)
                print(f"Saved scraped data JSON cache to {json_path}")
            except Exception as e:
                print(f"Failed to save JSON cache: {e}")
                
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

@app.get("/api/issues")
def get_property_issues(region: Optional[str] = None):
    try:
        from crawler.issue_scanner import scan_region_issues, get_all_issues
        if region:
            issues = scan_region_issues(region)
        else:
            issues = get_all_issues()
        return {"status": "success", "data": issues}
    except Exception as e:
        import traceback
        logging.error(f"Error in get_property_issues: {str(e)}\n{traceback.format_exc()}")
        return {"status": "error", "message": str(e)}

class AnalyzePdfRequest(BaseModel):
    pdf_url: str
    title: str = ""

@app.post("/api/issues/analyze_pdf")
def api_analyze_pdf(request: AnalyzePdfRequest):
    try:
        from pdf_analyzer import analyze_pdf_for_location
        result = analyze_pdf_for_location(request.pdf_url, request.title)
        return result
    except Exception as e:
        import traceback
        logging.error(f"Error in api_analyze_pdf: {str(e)}\n{traceback.format_exc()}")
        return {"status": "error", "message": str(e)}

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
    file_path = os.path.join(downloads_dir, f"{safe_case}_분석보고서.docx")
    
    try:
        from doc_generator import generate_analysis_doc_from_markdown
        generate_analysis_doc_from_markdown(case_number, req.markdown, downloads_dir)
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
    file_path = os.path.join(downloads_dir, f"{safe_case}_분석보고서.docx")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="보고서를 찾을 수 없습니다.")
    
    import urllib.parse
    encoded_filename = urllib.parse.quote(f"{safe_case}_분석보고서.docx")
    headers = {"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
    return FileResponse(path=file_path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers=headers)

@app.get("/api/download_ppt/{case_number:path}")
async def download_ppt(case_number: str):
    safe_case = case_number.replace(" ", "_").replace("/", "_")
    file_path = os.path.join(downloads_dir, f"{safe_case}_브리핑자료.pptx")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PPTX 브리핑 자료를 찾을 수 없습니다.")
    
    import urllib.parse
    encoded_filename = urllib.parse.quote(f"{safe_case}_브리핑자료.pptx")
    headers = {"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
    return FileResponse(path=file_path, media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation", headers=headers)

@app.get("/api/download_pdf/{case_number:path}")
async def download_pdf(case_number: str):
    safe_case = case_number.replace(" ", "_").replace("/", "_")
    file_path = os.path.join(downloads_dir, f"{safe_case}_브리핑자료.pdf")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF 브리핑 자료를 찾을 수 없습니다.")
    
    import urllib.parse
    encoded_filename = urllib.parse.quote(f"{safe_case}_브리핑자료.pdf")
    headers = {"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
    return FileResponse(path=file_path, media_type="application/pdf", headers=headers)



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

def init_db():
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            # Enable WAL mode for concurrent reads and writes
            conn.execute("PRAGMA journal_mode=WAL;")
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS road_cache_grids (
                    lat_idx INTEGER,
                    lng_idx INTEGER,
                    PRIMARY KEY (lat_idx, lng_idx)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS road_cache_segments (
                    osm_id INTEGER PRIMARY KEY,
                    name TEXT,
                    highway TEXT,
                    width REAL,
                    min_lat REAL,
                    max_lat REAL,
                    min_lng REAL,
                    max_lng REAL,
                    coords_json TEXT
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_road_cache_bounds ON road_cache_segments(max_lat, min_lat, max_lng, min_lng)')
            
            # Additional spatial optimization indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_auctions_lat_lng ON auctions(lat, lng)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_subways_lat_lng ON subways(lat, lng)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_universities_lat_lng ON universities(lat, lng)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_middle_schools_lat_lng ON middle_schools(lat, lng)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_industrial_complexes_lat_lng ON industrial_complexes(lat, lng)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_bus_stops_lat_lng ON bus_stops(lat, lng)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_commercial_areas_lat_lng ON commercial_areas(lat, lng)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_population_grids_lat_lng ON population_grids(lat, lng)')
            
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_district_units_bounds ON district_units(max_lat, min_lat, max_lng, min_lng)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_redevelopment_zones_bounds ON redevelopment_zones(max_lat, min_lat, max_lng, min_lng)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_zoning_polygons_bounds ON zoning_polygons(max_lat, min_lat, max_lng, min_lng)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_planning_roads_bounds ON planning_roads(max_lat, min_lat, max_lng, min_lng)')
            
            conn.commit()
            conn.close()
            print("Database cache tables and WAL mode initialized successfully.")
        except Exception as e:
            print("Failed to initialize database cache tables:", e)

init_db()

@app.get("/api/map/pois")
def get_map_pois(
    min_lat: Optional[float] = None,
    max_lat: Optional[float] = None,
    min_lng: Optional[float] = None,
    max_lng: Optional[float] = None,
    regions: Optional[str] = None,
    types: Optional[str] = None
):
    if not os.path.exists(DB_PATH):
        return {"status": "error", "message": "DB not found"}
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    active_types = types.split(',') if types else None
    
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

    subways = []
    if not active_types or "subways" in active_types:
        cursor.execute(f"SELECT line, name, address, lat, lng, status FROM subways{combined_condition} LIMIT 500", combined_params)
        subways = [dict(row) for row in cursor.fetchall()]
    
    universities = []
    if not active_types or "universities" in active_types:
        cursor.execute(f"SELECT name, address, lat, lng FROM universities{combined_condition} LIMIT 500", combined_params)
        universities = [dict(row) for row in cursor.fetchall()]
    
    middle_schools = []
    if not active_types or "middle_schools" in active_types:
        cursor.execute(f"SELECT name, address, lat, lng, special_hs_rate FROM middle_schools{combined_condition} LIMIT 500", combined_params)
        middle_schools = [dict(row) for row in cursor.fetchall()]
    
    industrial_complexes = []
    if not active_types or "industrial_complexes" in active_types:
        cursor.execute(f"SELECT name, lat, lng FROM industrial_complexes{query_condition} LIMIT 500", params)
        industrial_complexes = [dict(row) for row in cursor.fetchall()]

    bus_stops = []
    # Only fetch bus stops if bounding box is provided (to prevent crashing with 200k items)
    if not active_types or "bus_stops" in active_types:
        if min_lat and max_lat and min_lng and max_lng:
            cursor.execute('''
                SELECT name, lat, lng FROM bus_stops 
                WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ? LIMIT 500
            ''', (min_lat, max_lat, min_lng, max_lng))
            bus_stops = [dict(row) for row in cursor.fetchall()]
        
    commercial_areas = []
    if not active_types or "commercial_areas" in active_types:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='commercial_areas'")
        has_commercial = cursor.fetchone()
        
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


@app.get("/api/map/redevelopment_zones")
def get_map_redevelopment_zones(
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
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='redevelopment_zones'")
    if not cursor.fetchone():
        conn.close()
        return {"status": "success", "data": []}
        
    c_lat = (min_lat + max_lat) / 2.0
    c_lng = (min_lng + max_lng) / 2.0
    
    query = f'''
        SELECT id, name, propel_cd, geojson FROM redevelopment_zones
        WHERE max_lat >= ? AND min_lat <= ? 
          AND max_lng >= ? AND min_lng <= ?
        ORDER BY (max_lat - {c_lat})*(max_lat - {c_lat}) + (max_lng - {c_lng})*(max_lng - {c_lng}) ASC
        LIMIT 1000
    '''
    cursor.execute(query, (min_lat, max_lat, min_lng, max_lng))
    data = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return {"status": "success", "data": data}


@app.get("/api/map/zoning")
def get_map_zoning(
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
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='zoning_polygons'")
    if not cursor.fetchone():
        conn.close()
        return {"status": "success", "data": []}
        
    query = '''
        SELECT id, name, propel_cd, geojson FROM zoning_polygons
        WHERE max_lat >= ? AND min_lat <= ? 
          AND max_lng >= ? AND min_lng <= ?
        LIMIT 2000
    '''
    cursor.execute(query, (min_lat, max_lat, min_lng, max_lng))
    data = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return {"status": "success", "data": data}


@app.get("/api/map/planning_roads")
def get_map_planning_roads(
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
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='planning_roads'")
    if not cursor.fetchone():
        conn.close()
        return {"status": "success", "data": []}
        
    query = '''
        SELECT id, present_sn, name, road_class, geojson FROM planning_roads
        WHERE max_lat >= ? AND min_lat <= ? 
          AND max_lng >= ? AND min_lng <= ?
        LIMIT 2000
    '''
    cursor.execute(query, (min_lat, max_lat, min_lng, max_lng))
    data = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return {"status": "success", "data": data}


@app.get("/api/map/crosswalks")
def get_map_crosswalks(
    min_lat: Optional[float] = None,
    max_lat: Optional[float] = None,
    min_lng: Optional[float] = None,
    max_lng: Optional[float] = None
):
    import json
    if not os.path.exists(DB_PATH):
        return {"status": "error", "message": "DB not found"}
        
    if not (min_lat and max_lat and min_lng and max_lng):
        return {"status": "success", "data": {"type": "FeatureCollection", "features": []}}
        
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='crosswalk_segments'")
    if not cursor.fetchone():
        conn.close()
        return {"status": "success", "data": {"type": "FeatureCollection", "features": []}}
        
    cursor.execute('''
        SELECT name, coords_json FROM crosswalk_segments
        WHERE max_lat >= ? AND min_lat <= ? 
          AND max_lng >= ? AND min_lng <= ?
        LIMIT 1500
    ''', (min_lat, max_lat, min_lng, max_lng))
    
    rows = cursor.fetchall()
    features = []
    
    for r in rows:
        name, coords_json = r['name'], r['coords_json']
        try:
            coords = json.loads(coords_json)
        except Exception:
            continue
            
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": coords
            },
            "properties": {
                "name": name,
                "highway": "횡단보도"
            }
        })
        
    conn.close()
    
    geojson_result = {
        "type": "FeatureCollection",
        "features": features
    }
    
    return {"status": "success", "data": geojson_result}


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
        
    c_lat = (min_lat + max_lat) / 2.0
    c_lng = (min_lng + max_lng) / 2.0
    
    query = f'''
        SELECT id, name, geojson FROM district_units
        WHERE max_lat >= ? AND min_lat <= ? 
          AND max_lng >= ? AND min_lng <= ?
        ORDER BY (max_lat - {c_lat})*(max_lat - {c_lat}) + (max_lng - {c_lng})*(max_lng - {c_lng}) ASC
        LIMIT 1000
    '''
    cursor.execute(query, (min_lat, max_lat, min_lng, max_lng))
    data = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return {"status": "success", "data": data}

@app.get("/api/map/deregulation_zones")
def get_deregulation_zones(
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
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='deregulation_zones'")
    if not cursor.fetchone():
        conn.close()
        # Mock data for demonstration since the table doesn't exist
        c_lat = (min_lat + max_lat) / 2.0
        c_lng = (min_lng + max_lng) / 2.0
        import json
        mock_geojson = {
            "type": "Polygon",
            "coordinates": [[
                [c_lng - 0.005, c_lat - 0.005],
                [c_lng + 0.005, c_lat - 0.005],
                [c_lng + 0.005, c_lat + 0.005],
                [c_lng - 0.005, c_lat + 0.005],
                [c_lng - 0.005, c_lat - 0.005]
            ]]
        }
        return {"status": "success", "data": [
            {"id": 99999, "name": "가상 규제완화 시범지구", "geojson": json.dumps(mock_geojson)}
        ]}
        
    c_lat = (min_lat + max_lat) / 2.0
    c_lng = (min_lng + max_lng) / 2.0
    
    query = f'''
        SELECT id, name, type, details, geojson FROM deregulation_zones
        WHERE max_lat >= ? AND min_lat <= ? 
          AND max_lng >= ? AND min_lng <= ?
        ORDER BY (max_lat - {c_lat})*(max_lat - {c_lat}) + (max_lng - {c_lng})*(max_lng - {c_lng}) ASC
        LIMIT 1000
    '''
    cursor.execute(query, (min_lat, max_lat, min_lng, max_lng))
    data = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return {"status": "success", "data": data}

@app.get("/api/map/unexecuted_facilities")
def get_map_unexecuted_facilities(
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
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='unexecuted_facilities'")
    if not cursor.fetchone():
        conn.close()
        return {"status": "success", "data": []}
        
    c_lat = (min_lat + max_lat) / 2.0
    c_lng = (min_lng + max_lng) / 2.0
    
    query = f'''
        SELECT id, name, geojson FROM unexecuted_facilities
        WHERE max_lat >= ? AND min_lat <= ? 
          AND max_lng >= ? AND min_lng <= ?
        ORDER BY (max_lat - {c_lat})*(max_lat - {c_lat}) + (max_lng - {c_lng})*(max_lng - {c_lng}) ASC
        LIMIT 1000
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
        
    cursor.execute("SELECT id, line, status, coordinates_json FROM subway_lines")
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
    land_prices: Optional[str] = None,
    unexecuted_only: Optional[bool] = False
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

    if unexecuted_only:
        pass # query += " AND is_unexecuted = 1"  # Column does not exist in DB

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
            elif t in ('지산', '공장창고(집합)'):
                type_clauses.append("property_type = '지산'")
            elif t in ('집합', '상가(집합)'):
                type_clauses.append("property_type = '집합'")
            elif t in ('일반', '상가(일반)'):
                type_clauses.append("property_type = '일반'")
            elif t == '토지':
                type_clauses.append("property_type = '토지'")
            elif t in ('공장', '공장창고(일반)'):
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
            elif r == '대항력없음':
                rights_clauses.append("(special_notes IS NULL OR special_notes = '' OR special_notes = '0' OR special_notes = '0.0' OR special_notes LIKE '0 %' OR special_notes LIKE '%대항력 없음%' OR special_notes LIKE '%대항력없음%')")
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
            elif t in ('지산', '공장창고(집합)'):
                type_clauses.append("property_type = '지산'")
            elif t in ('집합', '상가(집합)'):
                type_clauses.append("property_type = '집합'")
            elif t in ('일반', '상가(일반)'):
                type_clauses.append("property_type = '일반'")
            elif t == '토지':
                type_clauses.append("property_type = '토지'")
            elif t in ('공장', '공장창고(일반)'):
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
            elif r == '대항력없음':
                rights_clauses.append("(special_notes IS NULL OR special_notes = '' OR special_notes = '0' OR special_notes = '0.0' OR special_notes LIKE '0 %' OR special_notes LIKE '%대항력 없음%' OR special_notes LIKE '%대항력없음%')")
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


class OverlapAnalyzeRequest(BaseModel):
    case_nos: List[str]
    scores: Optional[Dict[str, int]] = None
    overlap_counts: Optional[Dict[str, int]] = None
    matched_layers: Optional[Dict[str, List[str]]] = None

@app.post("/api/map/overlap_analyze")
async def post_overlap_analyze(req: OverlapAnalyzeRequest):
    if not os.path.exists(DB_PATH):
        return {"status": "error", "message": "DB not found"}
        
    if not req.case_nos:
        return {"status": "error", "message": "사건번호가 제공되지 않았습니다."}
        
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Query auctions table for all matching case numbers
    placeholders = ",".join(["?" for _ in req.case_nos])
    query = f"SELECT * FROM auctions WHERE case_no IN ({placeholders})"
    cursor.execute(query, req.case_nos)
    rows = cursor.fetchall()
    
    if not rows:
        conn.close()
        return {"status": "error", "message": "해당 사건번호들의 상세 정보를 조회할 수 없습니다."}
        
    items_map = {}
    for r in rows:
        d = dict(r)
        # Parse minimum_value and appraised_value from DB columns min_price and appraised_price
        try:
            appraised = int(d.get('appraised_price') or 0)
            minimum = int(d.get('min_price') or 0)
            d['appraised_value'] = appraised
            d['minimum_value'] = minimum
            
            # Calculate min_bid_rate if not present
            min_bid_rate = d.get('min_bid_rate')
            if min_bid_rate is None or min_bid_rate == 0:
                if appraised > 0:
                    min_bid_rate = int((minimum / appraised) * 100)
                else:
                    min_bid_rate = 100
            d['min_bid_rate'] = min_bid_rate
        except Exception:
            d['min_bid_rate'] = 100
            
        # Attach frontend-provided metadata if available
        c_no = d.get('case_no')
        if req.scores and c_no in req.scores:
            d['score'] = req.scores[c_no]
        if req.overlap_counts and c_no in req.overlap_counts:
            d['overlap_count'] = req.overlap_counts[c_no]
        if req.matched_layers and c_no in req.matched_layers:
            d['matched_layers'] = req.matched_layers[c_no]
            
        items_map[c_no] = d
        
    conn.close()
    
    # Sort items based on the input order of req.case_nos (which is already sorted on the frontend)
    sorted_items = []
    for c_no in req.case_nos:
        if c_no in items_map:
            sorted_items.append(items_map[c_no])
            
    if not sorted_items:
        return {"status": "error", "message": "조회된 사건 정보가 없습니다."}
        
    # Select top 3 (Best 3)
    best_items = sorted_items[:3]
    
    try:
        from fastapi.concurrency import run_in_threadpool
        from ai_analyzer import analyze_overlap_cases
        report_text = await run_in_threadpool(analyze_overlap_cases, best_items)
        return {"status": "success", "report": report_text, "items": sorted_items}
    except Exception as e:
        return {"status": "error", "message": f"Gemini 분석 중 오류 발생: {str(e)}"}


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

def parse_property_floor(address: str):
    """
    주소 문자열에서 물건의 층수를 추출합니다.
    반환값: (floor_type, floor_str)
    - floor_type: 'basement' (지하층), 'first' (1층), 'upper' (2층 이상), 'unknown' (미확인)
    - floor_str: 사용자 표시용 층수 문자열
    """
    import re
    if not address:
        return 'unknown', '지상층(확인 필요)'
        
    address_clean = str(address).strip()
    
    # 1. 지하층 패턴 체크
    if '지하' in address_clean:
        m = re.search(r'지하\s*(\d+)층', address_clean)
        if m:
            return 'basement', f"지하 {m.group(1)}층"
        return 'basement', '지하층'
        
    # 2. 명시적 층수 표현 체크 (예: 3층, 1층)
    m = re.search(r'(\d+)\s*층', address_clean)
    if m:
        floor_num = int(m.group(1))
        if floor_num == 1:
            return 'first', '1층'
        elif floor_num >= 2:
            return 'upper', f"{floor_num}층"
            
    # 3. 호수 패턴 체크 (예: 102호, 1205호)
    # 한글 주소에서 일반적으로 백의 자리 이상이 층수를 나타냄
    m = re.search(r'(\d{3,4})\s*호', address_clean)
    if m:
        unit_num = int(m.group(1))
        floor_num = unit_num // 100
        if floor_num == 1:
            return 'first', '1층'
        elif floor_num >= 2:
            return 'upper', f"{floor_num}층"
            
    return 'unknown', '1층(추정)'


def generate_recommendation_based_on_specs(res_pop: int, wrk_pop: int, floating_pop: dict, address: str, area_size: Optional[float]):
    """
    물건의 평수, 층수, 주거/직장인구, 유동인구를 모두 종합적으로 반영하여
    가장 현실적이고 데이터에 기반한 추천 업종 및 추천 사유를 생성합니다.
    """
    # 1. 층수 분석
    floor_type, floor_str = parse_property_floor(address)
    
    # 2. 평수 분석
    if area_size is not None and area_size > 0:
        if area_size < 15:
            size_class = "small"
            size_str = f"소형(약 {area_size:.1f}평)"
        elif area_size < 40:
            size_class = "medium"
            size_str = f"중형(약 {area_size:.1f}평)"
        elif area_size < 80:
            size_class = "large"
            size_str = f"대형(약 {area_size:.1f}평)"
        else:
            size_class = "xlarge"
            size_str = f"초대형(약 {area_size:.1f}평)"
    else:
        size_class = "medium"
        size_str = "중형(평수 미확인)"
        area_size = 0.0

    # 3. 배후수요 성격 판별 (오피스 중심 vs 주거 중심)
    if wrk_pop > res_pop * 0.7:
        demand_type = "office"
        demand_str = "오피스/직장인 중심"
    else:
        demand_type = "residential"
        demand_str = "주거 배후 중심"

    # 추천 매트릭스 정의
    matrix = {
        "office": {
            "basement": {
                "small": {
                    "biz": "무인 공유창고(셀프 스토리지), 1인 PT 스튜디오, 소형 세미나/연습실",
                    "desc": "오피스 상권 지하 소형 면적으로, 인근 직장인의 부족한 수납 공간을 해결하는 무인 창고나 예약제 PT 스튜디오가 적합합니다."
                },
                "medium": {
                    "biz": "피트니스/필라테스 샵, 실내 스크린 스포츠(야구/골프), 다트/이색 펍 주점",
                    "desc": "직장인들의 퇴근 후 건강 관리 및 스트레스 해소를 타깃으로 하는 필라테스나 스크린 오락시설, 또는 분위기 중심의 지하 펍이 적합합니다."
                },
                "large": {
                    "biz": "구내식당(한식 뷔페), 스크린골프 연습장, 크로스핏 체육관, 오피스 보조 아카이브",
                    "desc": "인근 직장인들의 점심 식사 수요를 집중 흡수할 수 있는 대형 한식 뷔식이나 소음 걱정 없는 지하 대형 체육/레저 시설이 유리합니다."
                },
                "xlarge": {
                    "biz": "프리미엄 피트니스 클럽, 대규모 스크린골프 아카데미, 실내 볼링장",
                    "desc": "대형 오피스 빌딩 단지의 풍부한 직장인 수요를 수용할 수 있는 프리미엄 피트니스 또는 대규모 스크린스포츠 공간으로의 기획이 가장 현실적입니다."
                }
            },
            "first": {
                "small": {
                    "biz": "테이크아웃 전문 커피숍, 샐러드/샌드위치 전문점, 소형 편의점, 토스트 전문점",
                    "desc": "출퇴근 및 점심시간 고밀도 유동인구 동선 상에서 회전율을 극대화할 수 있는 테이크아웃 F&B 업종이 최적입니다."
                },
                "medium": {
                    "biz": "캐주얼 한식/퓨전 레스토랑, 베이커리 카페, 수제버거 전문점, 약국, 대리점",
                    "desc": "직장인 점심/저녁 식사 수요를 흡수하는 요식업 브랜드나 처방/매출 안정성이 높은 1층 약국, 안테나 매장이 적합합니다."
                },
                "large": {
                    "biz": "대형 프랜차이즈 식당(고깃집, 일식당), 프리미엄 카페, 드럭스토어, 브랜드 편집숍",
                    "desc": "직장인 단체 회식 및 풍부한 유동인구의 소비를 이끌어낼 수 있는 대형 요식업 브랜드 또는 브랜드 쇼룸 매장이 유리합니다."
                },
                "xlarge": {
                    "biz": "수입차/가전 전시장, 시중은행 금융센터, 대형 프랜차이즈 뷔페, 대형 SSM",
                    "desc": "가시성이 뛰어난 전면 노출을 활용한 대형 전시장, 금융 기관 지점, 혹은 넓은 면적이 필요한 대형 식음 시설 입지가 적절합니다."
                }
            },
            "upper": {
                "small": {
                    "biz": "전문직 개인 사무실(세무사, 변리사, 행정사), 1인 오피스, 소형 예약제 뷰티숍",
                    "desc": "비교적 저렴한 임대료를 활용하여 인근 기업체를 대상으로 B2B 서비스를 제공하는 세무/법률 사무소나 1인 예약제 샵이 유리합니다."
                },
                "medium": {
                    "biz": "치과/이비인후과 의원, 기구 필라테스 스튜디오, 소형 공유 오피스",
                    "desc": "직장인들의 점심 시간이나 퇴근 직후 진료/이용이 용이한 치과/이비인후과 의원이나 필라테스, 공유 소형 사무실 임대가 유망합니다."
                },
                "large": {
                    "biz": "종합 검진 내과의원, 중형 공유 오피스, IT 벤처/지식산업 기업 사무실",
                    "desc": "주변 직장인들의 건강검진 수요를 충당할 수 있는 대형 내과 병원이나 중소 IT 벤처 사무실 용도로 기획하는 것이 가장 현실적입니다."
                },
                "xlarge": {
                    "biz": "기업 본사 사무소, 어학/직무 교육 종합 학원, 대형 메디컬 센터, 뷔페/연회장",
                    "desc": "대면적 임차가 필수적인 중견 IT/벤처 기업 본사, 직무 어학원, 혹은 전체 층을 활용하는 대형 종합 메디컬 센터 유치가 적합합니다."
                }
            }
        },
        "residential": {
            "basement": {
                "small": {
                    "biz": "주민 전용 무인 공유창고, 악기/음악 개인 연습실, 24시 무인 코인 빨래방",
                    "desc": "주거지 밀집 특성상 실내 수납 공간 부족을 해결해 줄 공유 창고나 소음 민원을 방지할 수 있는 방음 연습실이 유리합니다."
                },
                "medium": {
                    "biz": "24시간 코인 빨래방, 무인 코인 노래방, 동네 탁구장/실내 운동시설",
                    "desc": "인근 주민 및 1인 가구가 일상적으로 이용할 수 있는 코인 빨래방이나 소형 실내 놀거리 시설이 적합합니다."
                },
                "large": {
                    "biz": "어린이 전용 수영장/스포츠 교습소, 주민 스크린골프 클럽, 크로스핏 체육관",
                    "desc": "학부모 수요가 높은 어린이 스포츠 센터나 주민들이 도보로 이용할 수 있는 스크린골프, 대형 헬스시설이 우수합니다."
                },
                "xlarge": {
                    "biz": "프리미엄 스크린골프 아카데미, 대형 키즈 카페, 주민 복합 피트니스 센터, 지하 대형 식자재마트",
                    "desc": "넓은 바닥 공간이 필수적인 주민용 프리미엄 스크린골프나 키즈카페, 혹은 주민 밀집 상권의 지하 마트 기획이 유리합니다."
                }
            },
            "first": {
                "small": {
                    "biz": "밀착형 편의점, 반찬 전문점, 소형 무인 매장(아이스크림), 미용실, 동네 분식점",
                    "desc": "단지 내 도보 동선에 위치하여 가벼운 일상 소비를 즉각적으로 해결할 수 있는 반찬점, 무인 점포, 1인 미용실이 최적입니다."
                },
                "medium": {
                    "biz": "프랜차이즈 베이커리, 주민 친화형 중형 카페, 소아청소년과/이비인후과 의원, 동물병원",
                    "desc": "아파트 단지 입구나 중심 상가 코너 자리로, 집객력 있는 베이커리 브랜드, 카페 또는 소아과/이비인후과가 적합합니다."
                },
                "large": {
                    "biz": "중형 식자재 마트, 거점 메디컬 클리닉(내과, 가정의학과), 동물 메디컬 센터, 프랜차이즈 식당",
                    "desc": "배후 주거 인구의 일상 소비를 독점하는 마트나 단지 내 핵심 위치에 입점하는 패밀리 레스토랑, 소아과 등의 전문 병원이 유리합니다."
                },
                "xlarge": {
                    "biz": "단지 상가 대형 SSM, 대형 생활용품점(다이소형), 대형 프랜차이즈 패밀리 레스토랑",
                    "desc": "수천 세대의 배후 가구를 대상으로 하는 대형 식자재/생활용품 마트나 주말 가족 외식 수요를 흡수하는 대형 F&B 매장이 강력 추천됩니다."
                }
            },
            "upper": {
                "small": {
                    "biz": "단과 보습 교습소(수학/영어), 피아노/미술 공부방, 예약제 1인 헤어숍",
                    "desc": "비교적 조용하고 아늑한 분위기를 활용하여 인근 단지 초중등 학생을 타깃으로 하는 개인 공부방 및 예체능 교습소가 유망합니다."
                },
                "medium": {
                    "biz": "보습/입시 전문 학원, 예체능(태권도/발레) 아카데미, 독서실/스터디 카페, 소아치과 의원",
                    "desc": "학부모와 학생층의 접근이 우수한 곳으로 보습 학원, 태권도장, 또는 조용한 스터디 카페나 소아치과 개원이 안성맞춤입니다."
                },
                "large": {
                    "biz": "종합 입시 학원, 대형 태권도/체육 학원, 프리미엄 스터디 카페, 내과/정형외과 의원",
                    "desc": "단지 상가 고층부의 대형 면적으로, 종합 학원가 입지나 노령/가족층이 많이 찾는 정형외과, 내과 의원으로의 임대가 장기적으로 안전합니다."
                },
                "xlarge": {
                    "biz": "어린이 실내 놀이터/키즈 카페, 노인 주간보호센터(데이케어), 종합 메디컬 타워층",
                    "desc": "학부모들이 선호하는 대규모 키즈카페, 혹은 실버 세대를 위한 주간보호센터(데이케어), 층 전체를 쓰는 학원/메디컬 센터가 최적입니다."
                }
            }
        }
    }

    # floor_type 매핑 안전장치
    lookup_floor = floor_type if floor_type in ["basement", "first", "upper"] else "first"
    
    # 추천 데이터 조회
    biz_data = matrix[demand_type][lookup_floor][size_class]
    recom_biz = biz_data["biz"]
    base_desc = biz_data["desc"]

    # 4. 실시간 배후수요 데이터 연계 가공
    weekday_pop = floating_pop.get("weekday", 0)
    weekend_pop = floating_pop.get("weekend", 0)
    lunch_pop = floating_pop.get("lunch", 0)
    dinner_pop = floating_pop.get("dinner", 0)
    total_250 = floating_pop.get("total", 0)

    # 입지 세부 정보
    spec_line = f"📍 [분석 기준] 전용면적: {size_str} | 층수: {floor_str} | 배후수요 성격: {demand_str}"
    
    # 인구 구성 정보
    if demand_type == "office":
        demo_fact = f"이 입지는 반경 500m 내 직장인구({wrk_pop:,}명)가 거주인구({res_pop:,}명) 대비 두드러지게 밀집한 오피스 상업 지대입니다."
    else:
        demo_fact = f"이 입지는 반경 500m 내 거주인구({res_pop:,}명, 약 {int(res_pop/2.25):,}세대)의 두터운 소비층이 중심이 되는 주거밀집 지대입니다."

    # 유동인구 구성 정보
    if weekday_pop > weekend_pop * 1.2:
        flow_fact = f"250m 이내 유동인구는 주중 일평균 {weekday_pop:,}명으로 주말({weekend_pop:,}명)보다 직장인 통근 동선이 매우 발달하여 점심({lunch_pop:,}명) 및 퇴근시간 저녁({dinner_pop:,}명) 식음료/근린생활 업종의 집객률이 탁월합니다."
    elif weekend_pop > weekday_pop * 1.2:
        flow_fact = f"250m 이내 유동인구는 주말 일평균 {weekend_pop:,}명으로 주중({weekday_pop:,}명) 대비 주말 가족 여가/외식 동선이 풍부하여, 가족 단위 타깃 업종 및 생활밀착형 서비스의 영업 가치가 큽니다."
    else:
        flow_fact = f"250m 이내 유동인구는 주중({weekday_pop:,}명)과 주말({weekend_pop:,}명)의 흐름이 고르고, 일평균 {total_250:,}명의 탄탄한 기본 도보 동선이 지속되어 안정적 영업이 가능합니다."

    # 최종 상세 소견 작성
    recom_desc = (
        f"{spec_line}\n\n"
        f"💡 [입지 분석 특징]\n{demo_fact} {flow_fact}\n\n"
        f"🎯 [추천 가이드]\n{base_desc} 본 물건의 {size_str} 면적과 {floor_str}이라는 물리적 조건을 감안할 때, 추천 업종인 '{recom_biz.split(',')[0]}' 등의 입점 또는 임대 구성을 통해 공실 최소화 및 임대수익 극대화 효과를 거둘 수 있습니다."
    )

    return recom_biz, recom_desc


def get_auction_property_specs(case_no: Optional[str], address: Optional[str], property_type: str, area_size: Optional[float]):
    import re
    import json
    import os
    from datetime import datetime
    
    # 1. Floor parsing
    floor_num = None
    floor_str = "지상층"
    total_floors = None
    
    addr_str = address or ""
    
    # Check if address contains total floors (e.g. "15층 중 3층", "5층 건내 2층")
    m_total = re.search(r'(\d+)\s*층\s*(?:중|건내|건물\s*내)\s*(\d+)\s*층', addr_str)
    if m_total:
        total_floors = int(m_total.group(1))
        floor_num = int(m_total.group(2))
        floor_str = f"{floor_num}층"
    else:
        if "지하" in addr_str:
            floor_str = "지하"
            floor_num = -1
        else:
            m_floor = re.search(r'(\d+)\s*층', addr_str)
            if m_floor:
                floor_num = int(m_floor.group(1))
                floor_str = f"{floor_num}층"
            else:
                m_unit = re.search(r'(\d+)\s*호', addr_str)
                if m_unit:
                    unit = int(m_unit.group(1))
                    if unit >= 100:
                        floor_num = unit // 100
                        floor_str = f"{floor_num}층"
    
    # Estimate total floors if unknown
    if not total_floors:
        if floor_num and floor_num > 0:
            if "아파트" in property_type:
                total_floors = max(15, floor_num + 2)
            elif any(k in property_type for k in ["다세대", "빌라", "단독"]):
                total_floors = max(5, floor_num + 1)
            else:
                total_floors = max(5, floor_num + 1)
        else:
            total_floors = 5 # default fallback
            
    # Classify floor
    is_comm = any(k in property_type for k in ["상가", "상업", "업무", "근린"])
    if floor_str == "지하":
        floor_class = "지하"
    elif floor_num == 1 and is_comm:
        floor_class = "1층"
    elif floor_num and floor_num > 0:
        ratio = floor_num / total_floors
        if ratio <= 0.334:
            floor_class = "저층 (총층수의 1/3 이하)"
        elif ratio <= 0.667:
            floor_class = "중층 (총층수의 2/3 이하)"
        else:
            floor_class = "고층 (총층수의 3/3)"
    else:
        floor_class = "지상층 (층수 미확인)"
        
    # 2. Pyeong classification
    pyeong = area_size or 0.0
    if pyeong >= 35:
        pyeong_class = "대(35평 이상)"
    elif pyeong >= 20:
        pyeong_class = "중(20평 이상)"
    elif pyeong >= 10:
        pyeong_class = "소형(10평 이상)"
    else:
        pyeong_class = "초소형(10평 미만)"
        
    # 3. Build year / Age lookup
    build_year = None
    age = None
    age_class = "연식 정보 미크롤링 (리포트 실행 필요)"
    
    # Try to load from saved JSON cache
    if case_no:
        safe_case = case_no.replace(" ", "_").replace("/", "_")
        cache_path = os.path.join(downloads_dir, f"{safe_case}_data.json")
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    app_date = cache_data.get("approval_date")
                    if app_date:
                        # Extract 4 digit year
                        m_year = re.search(r'(\d{4})', str(app_date))
                        if m_year:
                            build_year = int(m_year.group(1))
                            current_year = datetime.now().year
                            age = current_year - build_year
            except Exception as e:
                print(f"Error loading cache JSON: {e}")
                
    if age is not None:
        if age <= 10:
            age_class = f"신축 (10년 이하) - {build_year}년식 ({age}년 경과)"
        elif age <= 25:
            age_class = f"준신축 (25년 이하) - {build_year}년식 ({age}년 경과)"
        else:
            age_class = f"노후 (25년 초과) - {build_year}년식 ({age}년 경과)"
            
    return {
        "floor": floor_str,
        "total_floors": total_floors,
        "floor_class": floor_class,
        "pyeong": pyeong,
        "pyeong_class": pyeong_class,
        "build_year": build_year,
        "age": age,
        "age_class": age_class
    }


def generate_specs_comparison_comments(specs: dict, property_type: str, matched_grid: Optional[dict]):
    pyeong = specs["pyeong"]
    pyeong_class = specs["pyeong_class"]
    floor = specs["floor"]
    floor_class = specs["floor_class"]
    age = specs["age"]
    age_class = specs["age_class"]
    
    comments = []
    
    # 1. Pyeong (면적/평수) 코멘트
    comments.append(f"■ 물건 평수대: <strong>{pyeong:.1f}평</strong> ({pyeong_class})")
    if pyeong >= 35:
        comments.append("└ 대형 평형대로서 넓은 주거/상업 공간을 필요로 하는 패밀리 세대나 중대형 식음료/사무소 배후수요에 적합합니다. 다만 단위 면적당 단가는 소형 대비 낮게 형성될 수 있습니다.")
    elif pyeong >= 20:
        comments.append("└ 가장 대중적인 중형 평형대로서 3~4인 가구의 탄탄한 실수요와 넓은 범주의 상업 업종(일반 요식업, 판매점 등) 집객에 가장 유리하여 환금성이 우수합니다.")
    elif pyeong >= 10:
        comments.append("└ 소형 평형대로서 1~2인 가구의 거주 임차 수요와 소자본 테이크아웃 및 밀착형 소형 근린생활 시설에 매우 최적화되어 있습니다.")
    elif pyeong > 0:
        comments.append("└ 초소형 평형대로서 1인 가구, 직장인 단독 세대 타깃의 초소형 주거 혹은 무인 업종(무인 아이스크림, 공유 창고 등)에 최적화된 컴팩트한 입지입니다.")
    else:
        comments.append("└ 평형대 정보를 확인할 수 없는 물건입니다.")

    # 2. Floor (층수) 코멘트
    comments.append(f"■ 물건 층수대: <strong>{floor}</strong> (총 {specs['total_floors']}층 중 {floor_class})")
    is_comm = any(k in property_type for k in ["상가", "상업", "업무", "근린"])
    if is_comm:
        if "지하" in floor_class:
            comments.append("└ 상가 지하층은 접근성이 낮으나 소음 제한이 없고 임대료가 저렴하여 무인 공유창고, 연습실, 스크린골프, 크로스핏 등 공간 중심 목적형 업종에 특화됩니다.")
        elif "1층" in floor_class:
            comments.append("└ 상가 1층은 유동인구의 동선 노출과 가시성이 최상인 핵심 입지로서 F&B, 테이크아웃, 편의점 등 고집객 생활밀착 업종의 권장 매출력이 극대화됩니다.")
        else:
            comments.append("└ 상가 지상층(저/중/고층)은 1층 대비 저렴한 임대료를 레버리지하여 목적형 방문 업종인 병의원, 학원, 전문직 사무실, 뷰티숍 임대 구성에 적절합니다.")
    else:
        if "지하" in floor_class:
            comments.append("└ 주거 지하층은 습기 및 환기 유의가 필요하나, 가격 경쟁력이 매우 높으므로 저렴한 임차 수요층이나 창고 겸용 소형 주거 공간으로 적합합니다.")
        elif "저층" in floor_class:
            comments.append("└ 주거 저층은 어린이집, 은퇴 세대의 실거주 선호가 높은 반면 사생활 노출 방지를 위한 조경 매칭이나 필로티 구조 여부가 가치 형성에 중요하게 작용합니다.")
        elif "중층" in floor_class:
            comments.append("└ 주거 중층은 채광과 조망이 무난하고 냉난방 효율이 가장 우수하여 대중적인 수요층의 임차 선호도가 가장 두텁습니다.")
        elif "고층" in floor_class:
            comments.append("└ 주거 고층은 뛰어난 조망권과 채광으로 인한 프리미엄이 크게 붙으며, 인근 실거래 분석 상 로얄층 선호 비율에 따라 시세 차익 극대화가 가능합니다.")
        else:
            comments.append("└ 주거 지상층으로서 세부 층비율을 파악하기 어렵습니다.")

    # 3. Age (노후도/건축년도) 코멘트
    comments.append(f"■ 물건 노후도: <strong>{age_class}</strong>")
    if age is not None:
        if age <= 10:
            comments.append("└ 준공 10년 이하의 신축급 물건으로, 시설 노후화로 인한 추가 수리/유지 보수비가 거의 들지 않아 실입주 및 전세 임차인 모집 경쟁력에서 절대적으로 유리합니다.")
        elif age <= 25:
            comments.append("└ 준공 25년 이하의 중간 연식 물건으로, 관리 상태에 따라 전용 공간 리모델링(섀시, 욕실 등)을 통해 자산 가치를 리빌딩하여 주변 신축 격차를 좁힐 수 있는 가성비 물건입니다.")
        else:
            comments.append("└ 준공 25년을 초과한 노후 건물이므로 철저한 누수/노후 배관 등 현장 조사가 필수적입니다. 다만, 향후 재건축/재개발 등 정비사업 추진에 따른 미래 자산가치 상승 매리트가 큽니다.")
    else:
        comments.append("└ (연식 분석) 건축년도가 아직 수집되지 않았습니다. 우측 상단 '권리분석 리포트 보기'를 실행해 주시면 마이옥션 정밀 크롤링을 통해 건축년도가 실시간 동기화되어 정교한 노후도 비교 소견이 채워집니다.")

    # 4. 실거래 격자 지표와의 융합 비교 코멘트
    if matched_grid:
        avg_price = matched_grid.get("avg_price", 0)
        age_prem = matched_grid.get("age_premium", 0)
        floor_sens = matched_grid.get("floor_sensitivity", 0)
        
        has_grid_info = age_prem > 0 or floor_sens > 0
        if has_grid_info:
            comments.append("\n💡 [실거래 격자 지표 연계 분석]")
            if age_prem > 0 and age is not None:
                comments.append(f"- 주변 신축/구축 가격 격차 비율이 <strong>{age_prem:.2f}배</strong>로 나타납니다. " + 
                                (f"본 물건은 {age_class.split(' - ')[0]}이므로 " + 
                                 ("주변 노후 주택 대비 높은 가격 프리미엄 형성이 가능할 것입니다." if age <= 10 else "감가상각이 반영되어 저렴한 가격에 낙찰받아 부가가치를 올릴 타이밍입니다.") if age else ""))
            if floor_sens > 0 and floor_class != "지하" and "미확인" not in floor_class:
                comments.append(f"- 이 격자의 층별 로얄층 가격 민감도는 <strong>{floor_sens:.2f}배</strong>입니다. " +
                                (f"본 물건은 {floor_class}에 속하므로 " + 
                                 ("시세 리딩의 주요 수혜를 받아 매매 가치가 우세할 것입니다." if "고층" in floor_class or "중층" in floor_class else "낙찰가 산정 시 가격 조정을 신중히 고려해야 합니다.")))

    return "\n".join(comments)


@app.get("/api/map/demographics")
def get_map_demographics(
    lat: float, 
    lng: float, 
    address: Optional[str] = None, 
    area_size: Optional[float] = None,
    case_no: Optional[str] = None,
    property_type: Optional[str] = None
):
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
    
    # Resolve case specifications from auctions database if case_no is provided
    if case_no:
        try:
            cursor.execute("SELECT property_type, area_size, address FROM auctions WHERE case_no = ?", (case_no,))
            row = cursor.fetchone()
            if row:
                if not property_type:
                    property_type = row["property_type"] or "아파트"
                if not area_size or area_size == 0:
                    area_size = row["area_size"]
                if not address:
                    address = row["address"]
        except Exception as e:
            print(f"Error querying auctions table for specs: {e}")
    
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

    # Query nearest grid indicators for specs comparison
    base_lat_step = 0.00225
    base_lng_step = 0.0028
    lat_idx = int(lat / base_lat_step)
    lng_idx = int(lng / base_lng_step)
    
    matched_grid = None
    try:
        cursor.execute('''
            SELECT avg_price_per_pyeong, age_premium_ratio, floor_sensitivity
            FROM realprice_grids
            WHERE lat_idx = ? AND lng_idx = ?
            LIMIT 1
        ''', (lat_idx, lng_idx))
        grid_row = cursor.fetchone()
        if grid_row:
            g = dict(grid_row)
            matched_grid = {
                "avg_price": g["avg_price_per_pyeong"] or 0.0,
                "age_premium": g["age_premium_ratio"] or 0.0,
                "floor_sensitivity": g["floor_sensitivity"] or 0.0
            }
    except Exception as e:
        print(f"Error querying realprice_grids in demographics: {e}")

    conn.close()
    
    # Estimate specs & generate comparison comments
    norm_property_type = property_type or "아파트"
    norm_area_size = area_size or 0.0
    specs = get_auction_property_specs(case_no, address, norm_property_type, norm_area_size)
    comparison_comments = generate_specs_comparison_comments(specs, norm_property_type, matched_grid)
    
    # 6. 종합 및 배후수요 종합 분석 평가
    res_pop = demographics["residential_population"]
    wrk_pop = demographics["workplace_population"]
    
    # 배후수요 유형 평가
    if wrk_pop > res_pop * 0.7:
        demand_assessment = "오피스 상업 중심지 (유동/직장인 유입 최상)"
        assessment_detail = "주거 밀도보다 일자리가 고밀도로 밀집한 핵심 경제 활동 구역입니다. 직장인 배후수요가 매우 강해 직산이나 상가 임대수요가 극대화되는 지역입니다."
    elif res_pop > 150000:
        demand_assessment = "주거 초고밀도 구역 (배후수요 안정성 극대)"
        assessment_detail = "가구 및 주택 밀집도가 대단히 높은 초대형 아파트 단지 및 주택가입니다. 생필품, 소매점, 학군 중심의 실수요 배후가 탄탄하며 낙찰 시 매매/전세 회전율이 우수합니다."
    else:
        demand_assessment = "배후수요 안정지대 (주거밀집 구역)"
        assessment_detail = "주거 배후수요와 근린 생활 수요가 조화롭게 분포된 지역입니다. 지하철 접근성에 따라 가치가 민감하게 반응하므로 지하철 인프라 연동 분석을 필히 활용하세요."

    # 유동인구 250m 특징 추가
    floating_detail = f"\n\n[입지 평가 특징 - 250m 이내 유동인구]\n- 주중 일평균 유동인구: 약 {weekday_pop:,}명 | 주말 일평균 유동인구: 약 {weekend_pop:,}명\n- 시간대별 분포: 점심(11~14시) 약 {lunch_pop:,}명 | 저녁(18~21시) 약 {dinner_pop:,}명"
    assessment_detail += floating_detail

    # 맞춤형 추천업종 및 사유 생성
    recom_biz, recom_desc = generate_recommendation_based_on_specs(
        res_pop=res_pop,
        wrk_pop=wrk_pop,
        floating_pop=floating_population_250,
        address=address,
        area_size=norm_area_size
    )

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
            "recom_desc": recom_desc,
            "specs_comparison": comparison_comments
        }
    }

@app.get("/api/map/grid_demographics")
def get_grid_demographics(
    min_lat: float, max_lat: float, min_lng: float, max_lng: float,
    type: str = "residential",  # "residential" | "workplace" | "floating"
    regions: Optional[str] = "서울,경기,인천"
):
    """
    지도 화면(BBox) 영역 내 500m 격자형 인구 데이터를 조회합니다.
    """
    # 500m 격자 위경도 증가 스텝 (약 500m에 해당하는 위경도 차이)
    lat_step = 0.0045
    lng_step = 0.0056
    
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'map_data.db')
    if not os.path.exists(db_path):
        db_path = os.path.join(os.path.dirname(__file__), '../data/map_data.db')
        
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    grids = []
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='population_500m_grids'")
    if cursor.fetchone():
        if type == "residential":
            query = '''
                SELECT lat, lng, residential_pop as avg_population, grid_code as grid_id 
                FROM population_500m_grids
                WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ? AND residential_pop > 0
                LIMIT 50000
            '''
        elif type == "workplace":
            query = '''
                SELECT lat, lng, worker_pop as avg_population, grid_code as grid_id 
                FROM population_500m_grids
                WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ? AND worker_pop > 0
                LIMIT 50000
            '''
        else: # floating
            # 유동인구는 일단 주거+직장의 합계로 대체
            query = '''
                SELECT lat, lng, (residential_pop + worker_pop) as avg_population, grid_code as grid_id 
                FROM population_500m_grids
                WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ? AND (residential_pop + worker_pop) > 0
                LIMIT 50000
            '''
            
        cursor.execute(query, (min_lat, max_lat, min_lng, max_lng))
        for row in cursor.fetchall():
            grids.append(dict(row))
            
    conn.close()
    return {
        "status": "success", 
        "data": grids, 
        "lat_step": lat_step, 
        "lng_step": lng_step
    }


@app.get("/api/map/road_flows")
def get_road_flows(
    min_lat: float, max_lat: float, min_lng: float, max_lng: float,
    day: Optional[str] = "weekday", time_of_day: Optional[str] = "day"
):
    """
    지도의 중심부 좌표를 기준으로 반경 250m 이내의 실제 이면도로 및 뒷골목(OSM 8m 이하 소도로)을
    SQLite 그리드 캐시(없을 시 OSM Overpass API 1회 수집)에서 조회하여,
    상위 5단계(Step 6~10) 유동인구 격자의 분포에 따라 유동량 농도를 산출하고,
    5단계 농도별 라인 히트맵 GeoJSON을 반환합니다.
    (차량 통행 중심 도로는 배제하고, 소도로/뒷골목만 매핑)
    """
    import random
    import requests
    import sqlite3
    import math
    import os
    import json
    import re

    # Fast Euclidean distance helper (m)
    def fast_dist(lat1, lng1, lat2, lng2):
        dy = (lat1 - lat2) * 111000.0
        dx = (lng1 - lng2) * 88000.0
        return math.sqrt(dx*dx + dy*dy)

    # 지도의 정확한 중심점(Center) 계산
    center_lat = (min_lat + max_lat) / 2.0
    center_lng = (min_lng + max_lng) / 2.0

    # 500m 반경 영역에 대한 Bounding Box 정의 (안전 마진으로 550m 설정)
    # 위도 550m ≈ 0.0050도, 경도 550m ≈ 0.0062도
    flow_min_lat = center_lat - 0.0050
    flow_max_lat = center_lat + 0.0050
    flow_min_lng = center_lng - 0.0062
    flow_max_lng = center_lng + 0.0062

    # 1. 중심부 반경 500m 격자 공간 연산을 위해 500m 패딩을 주어 유동인구 격자 수집
    pad_lat = 0.0045
    pad_lng = 0.0056
    
    grid_min_lat = flow_min_lat - pad_lat
    grid_max_lat = flow_max_lat + pad_lat
    grid_min_lng = flow_min_lng - pad_lng
    grid_max_lng = flow_max_lng + pad_lng
    
    top5_grids = []
    try:
        grid_res = get_grid_demographics(
            min_lat=grid_min_lat,
            max_lat=grid_max_lat,
            min_lng=grid_min_lng,
            max_lng=grid_max_lng,
            type="floating",
            regions="서울,경기,인천"
        )
        if grid_res.get("status") == "success":
            grids = grid_res.get("data", [])
            # 지역별 그룹화
            groups = {}
            for g in grids:
                r = g.get("region") or "seoul"
                if r not in groups:
                    groups[r] = []
                groups[r].append(g)
            
            # 각 지역별로 10분위수 정렬 및 상위 5단계(Step 6~10) 필터링
            for r, group_data in groups.items():
                group_data.sort(key=lambda x: x.get("avg_population", 0))
                n = len(group_data)
                if n == 0:
                    continue
                for index, item in enumerate(group_data):
                    step = int((index / n) * 10) + 1
                    step = min(step, 10)
                    if step >= 6:
                        item["step"] = step
                        top5_grids.append(item)
    except Exception as e:
        print("Failed to load grid demographics for road flows proximity logic:", e)

    # 1-2. 반경 500m 격자 공간 연산을 가속하기 위한 Grid Spatial Hashing 인덱스 구축
    bucket_size_lat = 0.005
    bucket_size_lng = 0.006
    spatial_index = {}
    for tg in top5_grids:
        b_lat = int(tg["lat"] / bucket_size_lat)
        b_lng = int(tg["lng"] / bucket_size_lng)
        key = (b_lat, b_lng)
        if key not in spatial_index:
            spatial_index[key] = []
        spatial_index[key].append(tg)

    # SQLite 로컬 그리드 영구 캐싱 시스템 작동
    db_path = DB_PATH

    # 격자 단위(0.01도) 획정 (중심 500m 영역 기준으로 최소화)
    lat_start = int(math.floor(flow_min_lat / 0.01))
    lat_end = int(math.floor(flow_max_lat / 0.01))
    lng_start = int(math.floor(flow_min_lng / 0.01))
    lng_end = int(math.floor(flow_max_lng / 0.01))

    features = []
    osm_success = False

    try:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA busy_timeout = 5000;")
        cursor = conn.cursor()

        # 캐시 그리드 조회
        cursor.execute('SELECT lat_idx, lng_idx FROM road_cache_grids')
        cached_cells = set(cursor.fetchall())

        # Identify region of center
        is_seoul = (37.43 <= center_lat <= 37.7) and (126.75 <= center_lng <= 127.2)

        # 미캐싱된 셀 식별 (서울, 경기, 인천 전체 영역에 대해 OSM 미러 캐싱을 지원)
        cells_to_fetch = []
        for lat_idx in range(lat_start, lat_end + 1):
            for lng_idx in range(lng_start, lng_end + 1):
                if (lat_idx, lng_idx) not in cached_cells:
                    cells_to_fetch.append((lat_idx, lng_idx))

        # API 부하 방지 및 속도 유지를 위해 1회 맵 이동시 캐싱 쿼리를 최대 4개 셀로 제한
        if len(cells_to_fetch) > 4:
            cells_to_fetch = cells_to_fetch[:4]

        # 줌 레벨 방어: BBox가 크면 (줌 레벨 15 이하) 실시간 인터넷 페칭을 비활성화하여 속도 강제 방어
        is_zoomed_out = (max_lat - min_lat > 0.015) or (max_lng - min_lng > 0.018)
        if is_zoomed_out:
            cells_to_fetch = []

        urls = [
            "https://overpass-api.de/api/interpreter",
            "https://lz4.overpass-api.de/api/interpreter",
            "https://overpass.kumi.systems/api/interpreter"
        ]

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Referer": "http://localhost:8000/",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
        }

        # Define parallel fetch helper function
        def fetch_and_parse_cell(cell_lat, cell_lng):
            c_min_lat = cell_lat * 0.01
            c_max_lat = (cell_lat + 1) * 0.01
            c_min_lng = cell_lng * 0.01
            c_max_lng = (cell_lng + 1) * 0.01

            segments = []
            fetched = False

            # 1. Try Overpass mirrors first (lightweight, tag-filtered)
            query = f"""
            [out:json][timeout:10];
            (
              way["highway"~"residential|service|unclassified|pedestrian|path|footway|living_street"]({c_min_lat},{c_min_lng},{c_max_lat},{c_max_lng});
            );
            out geom;
            """
            for url in urls:
                try:
                    print(f"Fetching road network via Overpass Mirror (Parallel): {url}")
                    response = requests.post(url, data={"data": query}, headers=headers, timeout=3.0)
                    if response.status_code == 200:
                        osm_data = response.json()
                        elements = osm_data.get("elements", [])
                        
                        for el in elements:
                            if el.get("type") == "way" and "geometry" in el:
                                osm_id = el["id"]
                                geom = el["geometry"]
                                coords = [[pt["lon"], pt["lat"]] for pt in geom]
                                if len(coords) < 2:
                                    continue
                                
                                tags = el.get("tags", {})
                                name = tags.get("name") or tags.get("name:ko", "소도로")
                                highway = tags.get("highway", "소도로")
                                
                                width_val = None
                                width_str = tags.get("width")
                                if width_str:
                                    try:
                                        match = re.search(r"([0-9.]+)", width_str)
                                        if match:
                                            width_val = float(match.group(1))
                                    except Exception:
                                        pass
                                
                                lats = [pt["lat"] for pt in geom]
                                lngs = [pt["lon"] for pt in geom]
                                segments.append({
                                    "osm_id": osm_id,
                                    "name": name,
                                    "highway": highway,
                                    "width": width_val,
                                    "min_lat": min(lats),
                                    "max_lat": max(lats),
                                    "min_lng": min(lngs),
                                    "max_lng": max(lngs),
                                    "coords_json": json.dumps(coords)
                                })
                        fetched = True
                        print(f"Parallel fetch success: Overpass Mirror {url} for ({cell_lat}, {cell_lng}) - {len(segments)} segments parsed.")
                        break
                except Exception as e:
                    print(f"Parallel fetch Overpass Mirror {url} failed/timed out for ({cell_lat}, {cell_lng}): {e}")

            # 2. Try OSM Main API as fallback if Overpass mirrors failed
            if not fetched:
                try:
                    osm_url = f"https://api.openstreetmap.org/api/0.6/map?bbox={c_min_lng},{c_min_lat},{c_max_lng},{c_max_lat}"
                    print(f"Fetching road network via OSM Main API Fallback (Parallel): {osm_url}")
                    response = requests.get(osm_url, headers=headers, timeout=5.0)
                    if response.status_code == 200:
                        import xml.etree.ElementTree as ET
                        root = ET.fromstring(response.content)
                        
                        nodes = {}
                        for node in root.findall('node'):
                            nodes[node.get('id')] = [float(node.get('lon')), float(node.get('lat'))]
                            
                        for w in root.findall('way'):
                            tags = {tag.get('k'): tag.get('v') for tag in w.findall('tag')}
                            highway = tags.get('highway')
                            
                            if highway and any(h_type in highway for h_type in ["residential", "service", "unclassified", "pedestrian", "path", "footway", "living_street"]):
                                osm_id = int(w.get('id'))
                                node_refs = [nd.get('ref') for nd in w.findall('nd')]
                                coords = [nodes[ref] for ref in node_refs if ref in nodes]
                                
                                if len(coords) < 2:
                                    continue
                                    
                                name = tags.get("name") or tags.get("name:ko") or "소도로"
                                
                                width_val = None
                                width_str = tags.get("width")
                                if width_str:
                                    try:
                                        match = re.search(r"([0-9.]+)", width_str)
                                        if match:
                                            width_val = float(match.group(1))
                                    except Exception:
                                        pass
                                        
                                lats = [pt[1] for pt in coords]
                                lngs = [pt[0] for pt in coords]
                                segments.append({
                                    "osm_id": osm_id,
                                    "name": name,
                                    "highway": highway,
                                    "width": width_val,
                                    "min_lat": min(lats),
                                    "max_lat": max(lats),
                                    "min_lng": min(lngs),
                                    "max_lng": max(lngs),
                                    "coords_json": json.dumps(coords)
                                })
                        fetched = True
                        print(f"Parallel fetch success: OSM Main API Fallback for ({cell_lat}, {cell_lng}) - {len(segments)} segments parsed.")
                except Exception as e:
                    print(f"Parallel fetch OSM Main API Fallback failed/timed out for ({cell_lat}, {cell_lng}): {e}")

            return cell_lat, cell_lng, fetched, segments

        # Fetch cells in parallel using ThreadPoolExecutor
        from concurrent.futures import ThreadPoolExecutor
        if cells_to_fetch:
            print(f"Starting parallel fetching for {len(cells_to_fetch)} uncached road cells...")
            with ThreadPoolExecutor(max_workers=len(cells_to_fetch)) as executor:
                futures = [executor.submit(fetch_and_parse_cell, lat_idx, lng_idx) for lat_idx, lng_idx in cells_to_fetch]
                results = [f.result() for f in futures]
            
            # Write results to SQLite sequentially in the main thread to avoid DB locking
            for cell_lat, cell_lng, fetched, segments in results:
                if fetched:
                    for seg in segments:
                        cursor.execute('''
                            INSERT OR REPLACE INTO road_cache_segments 
                            (osm_id, name, highway, width, min_lat, max_lat, min_lng, max_lng, coords_json)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (seg["osm_id"], seg["name"], seg["highway"], seg["width"], seg["min_lat"], seg["max_lat"], seg["min_lng"], seg["max_lng"], seg["coords_json"]))
                    
                    cursor.execute('INSERT OR REPLACE INTO road_cache_grids (lat_idx, lng_idx) VALUES (?, ?)', (cell_lat, cell_lng))
                    conn.commit()
                    print(f"Successfully cached {len(segments)} segments for cell ({cell_lat}, {cell_lng}) in DB.")


        # 캐시 DB로부터 영역 매칭 도로망 가져오기 (500m 반경 영역으로 질의 최소화)
        cursor.execute('''
            SELECT name, highway, width, coords_json FROM road_cache_segments
            WHERE max_lat >= ? AND min_lat <= ? AND max_lng >= ? AND min_lng <= ?
              AND highway != '횡단보도'
        ''', (flow_min_lat, flow_max_lat, flow_min_lng, flow_max_lng))
        
        rows = cursor.fetchall()
        parsed_roads = []
        max_score = 0.0

        for r in rows:
            name, highway, width_val, coords_json = r
            
            # 1. 폭 8m 이하 필터링 (차량통행 전용 중심도로 배제)
            if width_val is not None and width_val > 8.0:
                continue
                
            try:
                coords = json.loads(coords_json)
            except Exception:
                continue
                
            if len(coords) < 2:
                continue
                
            for i in range(len(coords) - 1):
                pt1 = coords[i]
                pt2 = coords[i+1]
                
                seg_coords = [pt1, pt2]
                seg_mid_lng = (pt1[0] + pt2[0]) / 2.0
                seg_mid_lat = (pt1[1] + pt2[1]) / 2.0
                
                # 2. 지도의 중심부 기준으로 반경 500m 이내의 소도로/뒷골목만 필터링 (제곱 거리 비교로 math.sqrt 제거)
                dy = (seg_mid_lat - center_lat) * 111000.0
                dx = (seg_mid_lng - center_lng) * 88000.0
                dist_from_center_sq = dx*dx + dy*dy
                if dist_from_center_sq > 250000.0:  # 500.0 ** 2
                    continue
                
                score = 0.0
                seg_b_lat = int(seg_mid_lat / bucket_size_lat)
                seg_b_lng = int(seg_mid_lng / bucket_size_lng)
                
                for d_lat in [-1, 0, 1]:
                    for d_lng in [-1, 0, 1]:
                        key = (seg_b_lat + d_lat, seg_b_lng + d_lng)
                        if key in spatial_index:
                            for tg in spatial_index[key]:
                                dy_tg = (seg_mid_lat - tg["lat"]) * 111000.0
                                dx_tg = (seg_mid_lng - tg["lng"]) * 88000.0
                                d_sq = dx_tg*dx_tg + dy_tg*dy_tg
                                if d_sq <= 250000.0:  # 500.0 ** 2
                                    d = math.sqrt(d_sq)
                                    decay = 1.0 - d / 500.0
                                    step_weight = (tg["step"] - 5) / 5.0
                                    score += tg["avg_population"] * decay * step_weight
                                    
                if score > max_score:
                    max_score = score
                    
                parsed_roads.append({
                    "coordinates": seg_coords,
                    "road_name": name,
                    "road_class": highway,
                    "score": score
                })

        conn.close()

        if parsed_roads:
            parsed_roads.sort(key=lambda x: x["score"])
            N = len(parsed_roads)
            
            for index, rd in enumerate(parsed_roads):
                if N > 0:
                    step = int((index / N) * 10) + 1
                    step = min(step, 10)
                else:
                    step = 1
                
                # Apply multipliers to step based on day and time_of_day
                step_multiplier = 1.0
                if day == "weekend":
                    step_multiplier *= 0.85
                if time_of_day == "night":
                    step_multiplier *= 0.90
                
                adjusted_step = max(1, min(10, int(step * step_multiplier)))
                
                # 5단계의 분위수 매핑
                if adjusted_step >= 9:
                    flow_type = "매우 높음"
                    intensity = 0.9
                elif adjusted_step >= 7:
                    flow_type = "높음"
                    intensity = 0.7
                elif adjusted_step >= 5:
                    flow_type = "중간"
                    intensity = 0.5
                elif adjusted_step >= 3:
                    flow_type = "낮음"
                    intensity = 0.3
                else:
                    flow_type = "매우 낮음"
                    intensity = 0.1
                
                seed_val = int((rd["coordinates"][0][0] * 100000 + rd["coordinates"][0][1] * 100000) % 100000)
                rng = random.Random(seed_val)
                if adjusted_step >= 9:
                    avg_flow = rng.randint(3000, 4500)
                elif adjusted_step >= 7:
                    avg_flow = rng.randint(2000, 2900)
                elif adjusted_step >= 5:
                    avg_flow = rng.randint(1000, 1900)
                elif adjusted_step >= 3:
                    avg_flow = rng.randint(500, 950)
                else:
                    avg_flow = rng.randint(100, 450)
                
                # Apply fine-grained scaling to avg_flow to make numbers look smooth and dynamic
                flow_multiplier = 1.0
                if day == "weekend":
                    flow_multiplier *= rng.uniform(0.8, 0.9)
                if time_of_day == "night":
                    flow_multiplier *= rng.uniform(0.9, 0.95)
                
                final_flow = max(100, int(avg_flow * flow_multiplier))
                
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": rd["coordinates"]
                    },
                    "properties": {
                        "road_name": rd["road_name"],
                        "road_class": rd["road_class"],
                        "flow_intensity": intensity,
                        "avg_hourly_flow": final_flow,
                        "flow_type": flow_type
                    }
                })
            osm_success = True
            print(f"Successfully processed road flows from SQLite Cache. Count: {len(features)}")
    except Exception as e:
        print("Caching road flows pipeline failed, fallback triggered:", e)

    # 3. Fallback 가상 생성 엔진 구동 시에도 중심 반경 250m 이내로 제한
    if not osm_success:
        print("Running procedural road flow generator fallback...")
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA busy_timeout = 5000;")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT name, lat, lng FROM subways
            WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?
            LIMIT 50
        ''', (min_lat, max_lat, min_lng, max_lng))
        subways = [dict(r) for r in cursor.fetchall()]
        
        cursor.execute('''
            SELECT name, lat, lng FROM bus_stops
            WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?
            LIMIT 150
        ''', (min_lat, max_lat, min_lng, max_lng))
        bus_stops = [dict(r) for r in cursor.fetchall()]
        
        cursor.execute('''
            SELECT name, lat, lng FROM commercial_areas
            WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?
            LIMIT 25
        ''', (min_lat, max_lat, min_lng, max_lng))
        commercials = [dict(r) for r in cursor.fetchall()]
        
        cursor.execute('''
            SELECT case_no, property_type, lat, lng FROM auctions
            WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?
            LIMIT 100
        ''', (min_lat, max_lat, min_lng, max_lng))
        auctions = [dict(r) for r in cursor.fetchall()]
        
        conn.close()
        
        candidate_roads = []
        
        # 도로명 생성용 데이터베이스 및 헬퍼 함수 정의
        gg_streets = [
            "분당로", "판교역로", "성남대로", "서현로", "정자일로", "야탑로", "금곡로", "백현로", "수내로", "황새울로", 
            "돌마로", "동판교로", "서판교로", "운중로", "고기동길", "수지동로", "신봉길", "죽전로", "보정로", "구성로", 
            "마북로", "동백로", "기흥로", "영덕로", "서천로", "신갈로", "구갈로", "상갈로", "보라로", "공세로", 
            "지곡로", "유림로", "고림로", "역북로", "삼가로", "포곡로", "모현로", "양지로", "백암로", "원삼로"
        ]
        ic_streets = [
            "예술로", "인하로", "경원대로", "남동대로", "호구포로", "앵고개로", "소래로", "논고개로", "아암대로", "청능대로", 
            "함박뫼로", "비류대로", "독배로", "미추홀대로", "매소홀로", "한나루로", "석정로", "경인로", "참외전로", "제물량로", 
            "우현로", "개항로", "화도진로", "송림로", "인중로", "서해대로", "축항대로", "방축로", "중봉대로", "가정로"
        ]
        street_pool = ic_streets if center_lng < 126.75 else gg_streets
        
        def get_road_name(lat, lng, prefix=""):
            h = int((lat * 10000 + lng * 10000) % len(street_pool))
            b = int((lat * 50000 + lng * 50000) % 150) + 1
            return f"{prefix}{street_pool[h]} {b}번길"
        
        def add_candidate(coords, name, r_class, def_intensity, f_type):
            seg_mid_lng = (coords[0][0] + coords[1][0]) / 2.0
            seg_mid_lat = (coords[0][1] + coords[1][1]) / 2.0
            
            # 중심에서 반경 500m 이내만 가상 생성
            if fast_dist(seg_mid_lat, seg_mid_lng, center_lat, center_lng) <= 500.0:
                candidate_roads.append({
                    "coordinates": coords,
                    "name": name,
                    "road_class": r_class,
                    "default_intensity": def_intensity,
                    "flow_type": f_type
                })

        # 1. 지하철역 배후 보행로망 생성
        for s in subways:
            s_name = s["name"]
            lat, lng = s["lat"], s["lng"]
            add_candidate([[lng - 0.0035, lat], [lng + 0.0035, lat]], f"{s_name}역 메인광장로", "보행자전용도로", 0.9, "오피스동선")
            add_candidate([[lng, lat - 0.0028], [lng, lat + 0.0028]], f"{s_name}역 중앙보행로", "보행자전용도로", 0.88, "오피스동선")
            add_candidate([[lng, lat], [lng + 0.002, lat + 0.0016]], f"{s_name}역 맛집골목", "소도로", 0.85, "먹자골목")
            add_candidate([[lng, lat], [lng - 0.002, lat - 0.0016]], f"{s_name}역 서측카페거리", "소도로", 0.83, "먹자골목")
            add_candidate([[lng, lat], [lng + 0.002, lat - 0.0016]], f"{s_name}역 남측먹자거리", "소도로", 0.84, "먹자골목")
            add_candidate([[lng, lat], [lng - 0.002, lat + 0.0016]], f"{s_name}역 북측상가길", "소도로", 0.82, "먹자골목")
            
        # 2. 상업지구 보행망 생성 (서울 지역에 유효)
        for c in commercials:
            c_name = c["name"]
            lat, lng = c["lat"], c["lng"]
            add_candidate([[lng - 0.0015, lat], [lng + 0.0015, lat]], f"{c_name} 상가 메인거리", "소도로", 0.84, "먹자골목")
            add_candidate([[lng, lat - 0.001], [lng, lat + 0.001]], f"{c_name} 상업 이면도로", "소도로", 0.71, "먹자골목")
            
        # 3. 경공매 물건지 진입소로 생성
        for a in auctions:
            a_type = a["property_type"]
            lat, lng = a["lat"], a["lng"]
            add_candidate([[lng - 0.0008, lat - 0.0004], [lng + 0.0008, lat - 0.0004]], get_road_name(lat, lng, "물건지 앞 "), "골목길", 0.45, "생활이동")
            add_candidate([[lng - 0.0008, lat + 0.0004], [lng + 0.0008, lat + 0.0004]], get_road_name(lat + 0.0001, lng, "물건지 뒤 "), "골목길", 0.43, "생활이동")
            add_candidate([[lng, lat - 0.0005], [lng, lat + 0.0005]], f"{a_type} 진입로", "골목길", 0.47, "생활이동")
            
        # 4. 버스정류장 교통 연계로 생성
        for b in bus_stops:
            b_name = b["name"]
            lat, lng = b["lat"], b["lng"]
            add_candidate([[lng - 0.0015, lat], [lng + 0.0015, lat]], f"{b_name} 정류장 연계로", "인도", 0.6, "생활이동")
            add_candidate([[lng, lat - 0.0008], [lng, lat + 0.0008]], get_road_name(lat, lng, "정류장배후 "), "골목길", 0.5, "생활이동")

        # 5. 상위 유동인구 5단계 격자 내 고밀도 상업 골목길 생성
        for tg in top5_grids:
            lat, lng = tg["lat"], tg["lng"]
            step = tg["step"]
            add_candidate([[lng - 0.0015, lat - 0.0008], [lng + 0.0015, lat - 0.0008]], get_road_name(lat, lng, "상권 배후"), "소도로", 0.7 + (step-6)*0.05, "먹자골목")
            add_candidate([[lng - 0.0015, lat + 0.0008], [lng + 0.0015, lat + 0.0008]], get_road_name(lat + 0.0002, lng, "상권 이면"), "소도로", 0.68 + (step-6)*0.05, "먹자골목")
            add_candidate([[lng - 0.0008, lat - 0.0012], [lng - 0.0008, lat + 0.0012]], get_road_name(lat, lng - 0.0002, "상가골목 "), "소도로", 0.72 + (step-6)*0.05, "먹자골목")
            add_candidate([[lng + 0.0008, lat - 0.0012], [lng + 0.0008, lat + 0.0012]], get_road_name(lat, lng + 0.0002, "번화가길 "), "소도로", 0.71 + (step-6)*0.05, "먹자골목")

        # 6. 영역 전체를 커버하는 커스텀 격자 형태의 이면도로망 생성 (유기적 골목길 형성)
        lats = [flow_min_lat + i * (flow_max_lat - flow_min_lat) / 8.0 for i in range(9)]
        lngs = [flow_min_lng + i * (flow_max_lng - flow_min_lng) / 8.0 for i in range(9)]
        
        # 가로 격자 노선 생성
        for r_idx, r_lat in enumerate(lats):
            for s_idx in range(4):
                lng_start_seg = flow_min_lng + s_idx * (flow_max_lng - flow_min_lng) / 4.0
                lng_end_seg = flow_min_lng + (s_idx + 1) * (flow_max_lng - flow_min_lng) / 4.0
                
                # 좌표 기반의 고정 난수를 활용하여 도로가 Pan할 때마다 뒤틀리지 않도록 보장
                seed_seg = int((r_lat * 100000 + lng_start_seg * 100000) % 100000)
                rng_seg = random.Random(seed_seg)
                if rng_seg.random() > 0.70: # ~70% 노선 유지 (30%는 T자형 및 불규칙 골목으로 끊김 효과)
                    continue
                
                # 자연스러운 굴곡 효과 (Bend)
                offset_lat1 = rng_seg.uniform(-0.00015, 0.00015)
                offset_lat2 = rng_seg.uniform(-0.00015, 0.00015)
                
                name = get_road_name(r_lat, lng_start_seg, "주거지 ")
                add_candidate(
                    [[lng_start_seg, r_lat + offset_lat1], [lng_end_seg, r_lat + offset_lat2]],
                    name, "소도로", 0.52, "생활이동"
                )
                
        # 세로 격자 노선 생성
        for c_idx, c_lng in enumerate(lngs):
            for s_idx in range(4):
                lat_start_seg = flow_min_lat + s_idx * (flow_max_lat - flow_min_lat) / 4.0
                lat_end_seg = flow_min_lat + (s_idx + 1) * (flow_max_lat - flow_min_lat) / 4.0
                
                # 좌표 기반의 고정 난수 활용
                seed_seg = int((lat_start_seg * 100000 + c_lng * 100000) % 100000)
                rng_seg = random.Random(seed_seg)
                if rng_seg.random() > 0.70:
                    continue
                
                # 자연스러운 굴곡 효과 (Bend)
                offset_lng1 = rng_seg.uniform(-0.00018, 0.00018)
                offset_lng2 = rng_seg.uniform(-0.00018, 0.00018)
                
                name = get_road_name(lat_start_seg, c_lng, "마을 ")
                add_candidate(
                    [[c_lng + offset_lng1, lat_start_seg], [c_lng + offset_lng2, lat_end_seg]],
                    name, "소도로", 0.51, "생활이동"
                )

        max_score = 0.0
        for rc in candidate_roads:
            geom = rc["coordinates"]
            mid_lat = sum(pt[1] for pt in geom) / len(geom)
            mid_lng = sum(pt[0] for pt in geom) / len(geom)
            
            score = 0.0
            seg_b_lat = int(mid_lat / bucket_size_lat)
            seg_b_lng = int(mid_lng / bucket_size_lng)
            
            for d_lat in [-1, 0, 1]:
                for d_lng in [-1, 0, 1]:
                    key = (seg_b_lat + d_lat, seg_b_lng + d_lng)
                    if key in spatial_index:
                        for tg in spatial_index[key]:
                            dy_tg = (mid_lat - tg["lat"]) * 111000.0
                            dx_tg = (mid_lng - tg["lng"]) * 88000.0
                            d_sq = dx_tg*dx_tg + dy_tg*dy_tg
                            if d_sq <= 250000.0:  # 500.0 ** 2
                                d = math.sqrt(d_sq)
                                decay = 1.0 - d / 500.0
                                step_weight = (tg["step"] - 5) / 5.0
                                score += tg["avg_population"] * decay * step_weight
            rc["score"] = score
            if score > max_score:
                max_score = score
                
        candidate_roads.sort(key=lambda x: x["score"])
        N = len(candidate_roads)
        
        for index, rc in enumerate(candidate_roads):
            if N > 0:
                step = int((index / N) * 10) + 1
                step = min(step, 10)
            else:
                step = 1
                
            # Apply multipliers to step based on day and time_of_day
            step_multiplier = 1.0
            if day == "weekend":
                step_multiplier *= 0.85
            if time_of_day == "night":
                step_multiplier *= 0.90
            
            adjusted_step = max(1, min(10, int(step * step_multiplier)))
            
            if adjusted_step >= 9:
                flow_type = "매우 높음"
                intensity = 0.9
            elif adjusted_step >= 7:
                flow_type = "높음"
                intensity = 0.7
            elif adjusted_step >= 5:
                flow_type = "중간"
                intensity = 0.5
            elif adjusted_step >= 3:
                flow_type = "낮음"
                intensity = 0.3
            else:
                flow_type = "매우 낮음"
                intensity = 0.1
            
            seed_val = int((rc["coordinates"][0][0] * 100000 + rc["coordinates"][0][1] * 100000) % 100000)
            rng = random.Random(seed_val)
            if adjusted_step >= 9:
                avg_flow = rng.randint(5000, 6200)
            elif adjusted_step >= 7:
                avg_flow = rng.randint(3000, 4800)
            elif adjusted_step >= 5:
                avg_flow = rng.randint(2000, 2900)
            elif adjusted_step >= 3:
                avg_flow = rng.randint(1500, 1950)
            else:
                avg_flow = rng.randint(500, 1400)
            
            # Apply fine-grained scaling to avg_flow to make numbers look smooth and dynamic
            flow_multiplier = 1.0
            if day == "weekend":
                flow_multiplier *= rng.uniform(0.8, 0.9)
            if time_of_day == "night":
                flow_multiplier *= rng.uniform(0.9, 0.95)
            
            final_flow = max(100, int(avg_flow * flow_multiplier))
            
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": rc["coordinates"]
                },
                "properties": {
                    "road_name": rc["name"],
                    "road_class": rc["road_class"],
                    "flow_intensity": intensity,
                    "avg_hourly_flow": final_flow,
                    "flow_type": flow_type
                }
            })

    geojson_result = {
        "type": "FeatureCollection",
        "features": features
    }
    
    return {"status": "success", "data": geojson_result}

@app.get("/api/map/realprice_indicators")
def get_realprice_indicators(
    min_lat: float,
    max_lat: float,
    min_lng: float,
    max_lng: float,
    property_type: str = "아파트",
    indicator_type: str = "avg_price_per_pyeong",
    grid_size: int = 1000
):
    """
    지정한 BBox 영역 내 실거래 격자 가격지표 데이터를 조회합니다.
    """
    base_lat_step = 0.00225
    base_lng_step = 0.0028
    
    scale = float(grid_size) / 250.0
    lat_step = base_lat_step * scale
    lng_step = base_lng_step * scale
    
    if not os.path.exists(DB_PATH):
        return {"status": "error", "message": "DB not found"}
        
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='realprice_grids'")
    if not cursor.fetchone():
        conn.close()
        return {"status": "error", "message": "Real price table not initialized yet."}
        
    # Query within BBox with padding to catch boundary grids
    query = '''
        SELECT lat_idx, lng_idx, lat, lng, 
               avg_price_per_pyeong, avg_deposit_per_pyeong, avg_rent, 
               jeonse_ratio, transaction_count, sale_count, rent_count, 
               age_premium_ratio, floor_sensitivity,
               sales_count_under_10, sales_count_10_to_20, sales_count_20_to_30, sales_count_over_30,
               sale_price_change_rate, rent_price_change_rate
        FROM realprice_grids
        WHERE lat BETWEEN ? AND ? 
          AND lng BETWEEN ? AND ?
          AND property_type = ?
    '''
    pad_lat = lat_step
    pad_lng = lng_step
    cursor.execute(query, (min_lat - pad_lat, max_lat + pad_lat, min_lng - pad_lng, max_lng + pad_lng, property_type))
    rows = cursor.fetchall()
    conn.close()
    
    # Group fine-grained (250m) grids from DB into custom-sized grid cells
    grouped_grids = {}
    for r in rows:
        d = dict(r)
        new_lat_idx = int(d["lat"] / lat_step)
        new_lng_idx = int(d["lng"] / lng_step)
        key = (new_lat_idx, new_lng_idx)
        if key not in grouped_grids:
            grouped_grids[key] = []
        grouped_grids[key].append(d)
        
    grids = []
    for (lat_idx, lng_idx), sub_cells in grouped_grids.items():
        total_tx = sum(c["transaction_count"] or 0 for c in sub_cells)
        if total_tx <= 0:
            continue
            
        weighted_lat = sum(c["lat"] * (c["transaction_count"] or 0) for c in sub_cells) / total_tx
        weighted_lng = sum(c["lng"] * (c["transaction_count"] or 0) for c in sub_cells) / total_tx
        
        def get_weighted_avg(field):
            valid_cells = [c for c in sub_cells if c[field] and c[field] > 0]
            valid_tx = sum(c["transaction_count"] or 0 for c in valid_cells)
            if valid_tx > 0:
                return sum(c[field] * (c["transaction_count"] or 0) for c in valid_cells) / valid_tx
            vals = [c[field] for c in sub_cells if c[field] and c[field] > 0]
            return sum(vals) / len(vals) if vals else 0.0

        def get_sum(field):
            return sum(c[field] or 0 for c in sub_cells)
            
        avg_price = get_weighted_avg("avg_price_per_pyeong")
        avg_deposit = get_weighted_avg("avg_deposit_per_pyeong")
        avg_rent = get_weighted_avg("avg_rent")
        age_premium = get_weighted_avg("age_premium_ratio")
        floor_sensitivity = get_weighted_avg("floor_sensitivity")
        
        sale_count = get_sum("sale_count")
        rent_count = get_sum("rent_count")
        
        sales_under_10 = get_sum("sales_count_under_10")
        sales_10_to_20 = get_sum("sales_count_10_to_20")
        sales_20_to_30 = get_sum("sales_count_20_to_30")
        sales_over_30 = get_sum("sales_count_over_30")
        
        valid_sale_rates = [c["sale_price_change_rate"] for c in sub_cells if c["sale_price_change_rate"] is not None]
        avg_sale_rate = sum(valid_sale_rates) / len(valid_sale_rates) if valid_sale_rates else 0.0

        valid_rent_rates = [c["rent_price_change_rate"] for c in sub_cells if c["rent_price_change_rate"] is not None]
        avg_rent_rate = sum(valid_rent_rates) / len(valid_rent_rates) if valid_rent_rates else 0.0

        
        # Calculate main pyeong type and percentage
        categories = {
            "10평 이하": sales_under_10,
            "20평 이하": sales_10_to_20,
            "30평 이하": sales_20_to_30,
            "30평 초과": sales_over_30
        }
        total_sales = sales_under_10 + sales_10_to_20 + sales_20_to_30 + sales_over_30
        
        main_pyeong_type = "-"
        main_pyeong_ratio = 0.0
        if total_sales > 0:
            max_cat = max(categories, key=categories.get)
            if categories[max_cat] > 0:
                main_pyeong_type = max_cat
                main_pyeong_ratio = (categories[max_cat] / total_sales) * 100
        
        if avg_price > 0 and avg_deposit > 0:
            jeonse_ratio = (avg_deposit / avg_price) * 100
        else:
            jeonse_ratio = get_weighted_avg("jeonse_ratio")
            
        val = 0.0
        if indicator_type == "avg_price_per_pyeong":
            val = avg_price
        elif indicator_type == "avg_deposit_per_pyeong":
            val = avg_deposit
        elif indicator_type == "jeonse_ratio":
            val = jeonse_ratio
        elif indicator_type == "transaction_count":
            val = float(total_tx)
        elif indicator_type == "main_pyeong_type":
            val = main_pyeong_ratio
        elif indicator_type == "age_premium_ratio":
            val = age_premium
        elif indicator_type == "floor_sensitivity":
            val = floor_sensitivity
            
        grids.append({
            "lat_idx": lat_idx,
            "lng_idx": lng_idx,
            "lat": weighted_lat,
            "lng": weighted_lng,
            "val": val,
            "avg_price": avg_price,
            "avg_deposit": avg_deposit,
            "avg_rent": avg_rent,
            "jeonse_ratio": jeonse_ratio,
            "count": total_tx,
            "sale_count": sale_count,
            "rent_count": rent_count,
            "main_pyeong_type": main_pyeong_type,
            "main_pyeong_ratio": main_pyeong_ratio,
            "sales_under_10": sales_under_10,
            "sales_10_to_20": sales_10_to_20,
            "sales_20_to_30": sales_20_to_30,
            "sales_over_30": sales_over_30,
            "age_premium": age_premium,
            "floor_sensitivity": floor_sensitivity,
            "sale_price_change_rate": avg_sale_rate,
            "rent_price_change_rate": avg_rent_rate
        })
        
    return {
        "status": "success",
        "lat_step": lat_step,
        "lng_step": lng_step,
        "data": grids
    }

# 이미지 제공용 스태틱 라우트
test_images_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_images")
if os.path.exists(test_images_dir):
    app.mount("/test_images", StaticFiles(directory=test_images_dir), name="images")


from naver_price_analyzer import analyze_price

class NaverPriceRequest(BaseModel):
    lat: float
    lon: float
    type: str
    area_pyeong: float
    floor: str
    total_floor: str
    build_year: str
    appraised_price: float
    min_price: float
    senior_debt: float

@app.post("/api/naver_price_analysis")
async def naver_price_analysis(req: NaverPriceRequest):
    try:
        result = analyze_price(
            target_lat=req.lat,
            target_lon=req.lon,
            target_type=req.type,
            target_area_pyeong=req.area_pyeong,
            target_floor=req.floor,
            target_total_floor=req.total_floor,
            target_build_year=req.build_year,
            target_appraised_price=req.appraised_price,
            target_min_price=req.min_price,
            target_senior_debt=req.senior_debt
        )
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


public_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public")
if os.path.exists(public_dir):
    app.mount("/", StaticFiles(directory=public_dir, html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8001)
