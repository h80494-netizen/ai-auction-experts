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
        parsed_data["address"] = data.get("address", "")
        parsed_data["status"] = data.get("status", "")
        
        # 감정가, 최저가는 getGongme에서는 minprice만 존재. 감정가는 기본적으로 첫 입찰가이거나 없는 경우 예외 처리
        parsed_data["minimum_value"] = str(data.get("minprice") or "")
        parsed_data["appraised_value"] = str(data.get("frstBidPrc") or data.get("minprice") or "")
        
        parsed_data["property_type"] = data.get("category", "") or data.get("cltrUsgLclsCtgrNm", "")
        
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
