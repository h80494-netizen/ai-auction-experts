import os
import asyncio
from playwright.async_api import async_playwright
import urllib.request
import re
from bs4 import BeautifulSoup

MADANGS_ID = "h80494"
MADANGS_PW = "spring11!!"

async def search_madangs_list(case_number: str):
    """
    마당스에서 사건번호(물건관리번호)로 기본 정보를 검색합니다.
    """
    clean_case = case_number.replace("-", "")
    target_url = f"https://madangs.com/goview?g_code={clean_case}"
    print(f"[{case_number}] 마당스 검색 시도: {target_url}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=50)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            await page.goto(target_url, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            # 주소 추출
            address = ""
            addr_elem = soup.select_one("span.top_main_address.after")
            if addr_elem:
                address = addr_elem.get_text(strip=True)
            elif soup.find(string=lambda t: t and "서울특별시" in t):
                # Fallback for address
                for tag in soup.find_all(string=lambda t: t and "서울특별시" in t):
                    if len(tag) > 10:
                        address = tag.strip()
                        break
            
            # 상태 추출
            status = ""
            state_elems = soup.select("span.state")
            for elem in state_elems:
                st = elem.get("data-state-text", "")
                if st and ("유찰" in st or "진행" in st or "수의계약" in st or "개찰" in st):
                    status = st
                    break
            if not status:
                for elem in state_elems:
                    if elem.text and ("유찰" in elem.text or "진행" in elem.text):
                        status = elem.text.strip()
                        break

            # 감정가, 최저가 추출
            appraised_value = ""
            minimum_value = ""
            
            # 텍스트 노드 순회하며 찾기
            text_nodes = soup.find_all(string=True)
            for i, text in enumerate(text_nodes):
                t = text.strip()
                if "감정가" in t and not appraised_value:
                    for j in range(1, 5):
                        if i + j < len(text_nodes):
                            val = text_nodes[i + j].strip()
                            if "원" in val:
                                appraised_value = val
                                break
                if "최저가" in t and not minimum_value:
                    for j in range(1, 10):
                        if i + j < len(text_nodes):
                            val = text_nodes[i + j].strip()
                            if "원" in val:
                                minimum_value = val
                                break
            
            items = []
            if address:
                items.append({
                    "address": address,
                    "status": status,
                    "raw_text": f"마당스 데이터: {address} {status}",
                    "appraised_value": appraised_value.replace(" ", ""),
                    "minimum_value": minimum_value.replace(" ", ""),
                    "approval_date": "",
                    "property_type": ""
                })
                return {"success": True, "items": items}
            else:
                return {"success": False, "message": "마당스에서 결과를 찾을 수 없습니다."}
                
        except Exception as e:
            print(f"마당스 검색 중 오류: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await browser.close()


async def scrape_madangs_case(case_number: str, address_hint: str = ""):
    """
    마당스에서 사건 상세 정보를 크롤링하고 전체 페이지를 PDF로 인쇄합니다.
    """
    clean_case = case_number.replace("-", "")
    target_url = f"https://madangs.com/goview?g_code={clean_case}"
    print(f"[{case_number}] 마당스 상세 크롤링 및 PDF 다운로드: {target_url}")
    
    download_dir = os.path.join(os.getcwd(), "downloads", case_number)
    os.makedirs(download_dir, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=50)
        context = await browser.new_context(viewport={'width': 1280, 'height': 2000})
        page = await context.new_page()
        
        try:
            # 1. 로그인
            print("마당스 로그인 시도 중...")
            await page.goto("https://madangs.com/member/login")
            try:
                await page.fill("input[name='id'], input[name='user_id'], input[type='text']", MADANGS_ID)
                await page.fill("input[type='password']", MADANGS_PW)
                await page.press("input[type='password']", "Enter")
                await page.wait_for_load_state("networkidle", timeout=5000)
            except Exception as e:
                print(f"로그인 폼 에러 (무시): {e}")

            # 2. 상세 페이지 이동
            print("상세 페이지 이동 중...")
            await page.goto(target_url, wait_until="networkidle", timeout=20000)
            await page.wait_for_timeout(3000)
            
            # PDF 저장 (권리분석용)
            pdf_path = os.path.join(download_dir, f"{case_number}_madangs_detail.pdf")
            await page.pdf(path=pdf_path, print_background=True)
            print(f"마당스 상세페이지 PDF 저장 완료: {pdf_path}")
            
            # HTML 파싱하여 기본 정보 추출
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            address = ""
            addr_elem = soup.select_one("span.top_main_address.after")
            if addr_elem: address = addr_elem.get_text(strip=True)
            
            status = ""
            state_elems = soup.select("span.state")
            for elem in state_elems:
                st = elem.get("data-state-text", "")
                if st and ("유찰" in st or "진행" in st or "수의계약" in st):
                    status = st
                    break
            
            appraised_value, minimum_value, property_type = "", "", ""
            text_nodes = soup.find_all(string=True)
            for i, text in enumerate(text_nodes):
                t = text.strip()
                if "감정가" in t and not appraised_value:
                    for j in range(1, 5):
                        if i+j < len(text_nodes) and "원" in text_nodes[i+j]:
                            appraised_value = text_nodes[i+j].strip()
                            break
                if "최저가" in t and not minimum_value:
                    for j in range(1, 10):
                        if i+j < len(text_nodes) and "원" in text_nodes[i+j]:
                            minimum_value = text_nodes[i+j].strip()
                            break
                if "용도" in t and not property_type:
                    for j in range(1, 5):
                        if i+j < len(text_nodes) and text_nodes[i+j].strip():
                            property_type = text_nodes[i+j].strip()
                            break
                            
            parsed_data = {
                "address": address,
                "status": status,
                "appraised_value": appraised_value.replace(" ", ""),
                "minimum_value": minimum_value.replace(" ", ""),
                "property_type": property_type,
                "downloaded_pdfs": [pdf_path],
                "images": []
            }
            
            # 3. 사진 다운로드 
            # 마당스 공매 상세 페이지 내의 사진들을 추출
            img_locators = page.locator("img.swiper_case_image")
            count = await img_locators.count()
            print(f"상세페이지 내 총 {count}개의 이미지 발견")
            
            target_filenames = ["photo.jpg", "map.jpg", "structure.jpg"]
            
            for i in range(count):
                if i >= len(target_filenames):
                    break
                src = await img_locators.nth(i).get_attribute("src")
                if not src:
                    continue
                if src.startswith("//"): src = "https:" + src
                elif src.startswith("/"): src = "https://madangs.com" + src
                
                filename = target_filenames[i]
                target_path = os.path.join(download_dir, filename)
                try:
                    req = urllib.request.Request(src, headers={'User-Agent': 'Mozilla/5.0'})
                    with open(target_path, 'wb') as f:
                        f.write(urllib.request.urlopen(req).read())
                    print(f"{filename} 다운로드 완료: {src}")
                    parsed_data["images"].append(target_path)
                except Exception as e:
                    print(f"{filename} 다운로드 실패: {e}")
                            
            return {"success": True, "data": parsed_data}
            
        except Exception as e:
            print(f"마당스 크롤링 실패: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await browser.close()


async def scrape_madangs_images(case_number: str, madangs_url: str):
    """
    기존 호환성을 유지하기 위한 팝업 URL 기반 이미지 크롤러
    """
    print(f"[{case_number}] 마당스 팝업 이미지 스크래핑 시작: {madangs_url}")
    
    download_dir = os.path.join(os.getcwd(), "downloads", case_number)
    os.makedirs(download_dir, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=50)
        context = await browser.new_context()
        page = await context.new_page()
        try:
            await page.goto("https://madangs.com/member/login")
            try:
                await page.fill("input[name='id'], input[name='user_id'], input[type='text']", MADANGS_ID)
                await page.fill("input[type='password']", MADANGS_PW)
                await page.press("input[type='password']", "Enter")
                await page.wait_for_load_state("networkidle", timeout=5000)
            except: pass

            await page.goto(madangs_url, wait_until="networkidle")
            await page.wait_for_timeout(2000)
            
            img_locators = page.locator("img")
            count = await img_locators.count()
            targets = {"전경": "photo.jpg", "위치도": "map.jpg", "내부구조도": "structure.jpg"}
            found_targets = []
            
            for i in range(count):
                src = await img_locators.nth(i).get_attribute("src")
                alt = await img_locators.nth(i).get_attribute("alt")
                if not src or not alt: continue
                alt_clean = alt.replace(" ", "")
                for key, filename in targets.items():
                    if key in alt_clean and filename not in found_targets:
                        if src.startswith("//"): src = "https:" + src
                        elif src.startswith("/"): src = "https://madangs.com" + src
                        target_path = os.path.join(download_dir, filename)
                        try:
                            req = urllib.request.Request(src, headers={'User-Agent': 'Mozilla/5.0'})
                            with open(target_path, 'wb') as f:
                                f.write(urllib.request.urlopen(req).read())
                            found_targets.append(filename)
                        except: pass
        except Exception as e:
            print(f"마당스 팝업 이미지 크롤링 중 오류 발생: {e}")
        finally:
            await browser.close()
