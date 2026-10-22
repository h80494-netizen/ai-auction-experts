import asyncio
import os
import urllib.request
import urllib.error
import json

ONBID_ID = "h80494"
ONBID_PW = "spring11!!"

def _fetch_auctionmsg_sync(case_number: str, download_dir: str):
    url = f"https://map.auctionmsg.com/server/api/?c=Gongme&m=getGongme&id={case_number}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": f"https://map.auctionmsg.com/gongme/detail/{case_number}"
    }
    
    parsed_data = {
        "address": "",
        "status": "",
        "appraised_value": "",
        "minimum_value": "",
        "property_type": "",
        "downloaded_pdfs": [],
        "images": []
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status != 200:
                return {"success": False, "message": f"경매알리미 API 호출 실패: {response.status}"}
            
            result = json.loads(response.read().decode('utf-8'))
            
        if not result or 'data' not in result or not result['data']:
            return {"success": False, "message": "검색 결과에서 물건을 찾을 수 없습니다."}
            
        data = result['data']
        
        # 기본 정보 매핑
        addr_base = data.get("address", "")
        cltr_nm = data.get("onbidCltrNm", "")
        # 물건명에 세부 호수(예: B1001호)가 포함되어 있으면 상세 주소로 활용
        if cltr_nm and any(k in cltr_nm for k in ["호", "층", "동", "지하", "B"]):
            parsed_data["address"] = cltr_nm
        else:
            parsed_data["address"] = addr_base
        parsed_data["status"] = data.get("status", "")
        
        # 감정가, 최저가 추출 (1순위: 감정가, 2순위: 1회차 입찰시작가, 3순위: 가장 빠른 입찰가/최저가)
        appraised = data.get("estimatedprice")
        if not appraised or str(appraised) == "0":
            appraised = data.get("frstBidPrc")
        if not appraised or str(appraised) == "0":
            appraised = data.get("minprice")
            
        parsed_data["appraised_value"] = str(appraised or "")
        parsed_data["minimum_value"] = str(data.get("minprice") or "")
        
        # 공매 재산종류 (압류재산, 신탁재산, 국유재산, 수의계약 등)
        prpt_div = data.get("prptDivNm", "")
        parsed_data["gongme_type"] = prpt_div if prpt_div else "기타일반재산(신탁 등)"
        
        # 세부 용도 및 부동산 유형
        scls_nm = data.get("cltrUsgSclsCtgrNm", "")
        mcls_nm = data.get("cltrUsgMclsCtgrNm", "")
        lcls_nm = data.get("cltrUsgLclsCtgrNm", "")
        category_nm = data.get("category", "")
        parsed_data["property_type"] = scls_nm or mcls_nm or category_nm or lcls_nm or "상가/근린시설"
        
        # 건물면적 및 대지면적 (㎡ -> 평 환산 매핑)
        bld_sqm_raw = data.get("bldSqms")
        land_sqm_raw = data.get("landSqms")
        
        building_area_str = "정보없음"
        building_pyeong = 0.0
        if bld_sqm_raw and str(bld_sqm_raw).strip() not in ["", "0", "null", "None"]:
            try:
                bld_sqm = float(bld_sqm_raw)
                building_pyeong = round(bld_sqm / 3.30578, 1)
                building_area_str = f"{bld_sqm:.2f}㎡ ({building_pyeong}평)"
            except Exception:
                building_area_str = str(bld_sqm_raw)
                
        land_area_str = "정보없음"
        land_pyeong = 0.0
        if land_sqm_raw and str(land_sqm_raw).strip() not in ["", "0", "null", "None"]:
            try:
                land_sqm = float(land_sqm_raw)
                land_pyeong = round(land_sqm / 3.30578, 1)
                land_area_str = f"{land_sqm:.2f}㎡ ({land_pyeong}평)"
            except Exception:
                land_area_str = str(land_sqm_raw)
                
        parsed_data["building_area"] = building_area_str
        parsed_data["building_pyeong"] = building_pyeong
        parsed_data["land_area"] = land_area_str
        parsed_data["land_pyeong"] = land_pyeong
        parsed_data["pyeong"] = building_pyeong
        parsed_data["area_size"] = building_pyeong
        parsed_data["land_size"] = land_pyeong
        
        # 이미지 (옵션)
        img_url = data.get("image")
        if img_url:
            parsed_data["images"].append(img_url)
            # 권리분석보고서(Word) 생성을 위해 로컬 다운로드 폴더에 사진 저장
            if download_dir:
                photo_path = os.path.join(download_dir, "photo.jpg")
                map_path = os.path.join(download_dir, "map.jpg")
                structure_path = os.path.join(download_dir, "structure.jpg")
                try:
                    img_req = urllib.request.Request(img_url, headers=headers)
                    with urllib.request.urlopen(img_req, timeout=10) as img_res:
                        img_data = img_res.read()
                        with open(photo_path, "wb") as f:
                            f.write(img_data)
                        # 공매는 사진이 1개뿐인 경우가 많으므로 동일한 사진을 복사하여 배치
                        with open(map_path, "wb") as f:
                            f.write(img_data)
                        with open(structure_path, "wb") as f:
                            f.write(img_data)
                except Exception as e:
                    print(f"[{case_number}] 사진 다운로드 실패: {e}")
        
        print(f"[{case_number}] 데이터 추출 완료: {parsed_data['address']}")
        return {"success": True, "data": parsed_data}
        
    except Exception as e:
        print(f"[{case_number}] 데이터 추출 중 에러: {e}")
        return {"success": False, "message": str(e)}

async def scrape_onbid_case_async(case_number: str):
    print(f"[{case_number}] 경매알리미 기반 크롤링 시작...")
    
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    download_dir = os.path.join(project_root, "downloads", case_number)
    os.makedirs(download_dir, exist_ok=True)
    
    # Run requests synchronously in a thread pool to avoid blocking asyncio
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, _fetch_auctionmsg_sync, case_number, download_dir)
    return result

def scrape_onbid_case(case_number: str, address_hint: str = "") -> dict:
    return asyncio.run(scrape_onbid_case_async(case_number))
