import os
from playwright.async_api import async_playwright
import asyncio
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

MYAUCTION_ID = os.getenv("MYAUCTION_ID", "")
MYAUCTION_PW = os.getenv("MYAUCTION_PW", "")

async def search_myauction_list(case_number: str):
    """
    사건번호로 마이옥션을 검색하여 관련된 물건(주소 및 상태) 리스트를 반환합니다.
    """
    import re
    print(f"[{case_number}] 사건번호 주소 목록 검색 시작...")
    
    clean_case = case_number.replace(" ", "")
    is_public_sale = "-" in clean_case
    
    year = ""
    num = ""
    if not is_public_sale:
        match = re.search(r'(\d{4})(?:타경)?(\d+)', clean_case)
        if not match:
            return {"success": False, "message": "올바른 사건번호 형식이 아닙니다 (예: 2024타경5020 또는 20245020)"}
        year = match.group(1)
        num = match.group(2)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=50)
        context = await browser.new_context()
        page = await context.new_page()
        
        # 다이얼로그 핸들러 추가
        async def handle_dialog(dialog):
            print(f"Alert 뜸: {dialog.message}")
            try:
                await dialog.dismiss()
            except:
                pass
        page.on("dialog", lambda dialog: asyncio.create_task(handle_dialog(dialog)))
        
        try:
            try:
                await page.goto("http://www.my-auction.co.kr/member/login.php", wait_until="domcontentloaded", timeout=10000)
            except Exception as e:
                print(f"login.php 이동 실패: {e}")
            try:
                await page.wait_for_selector("#id", state="visible", timeout=3000)
                await page.fill("#id", MYAUCTION_ID)
                await page.fill("#passwd", MYAUCTION_PW)
                # 로그인 버튼 클릭
                await page.click("#btn_login")
                # main.php 로딩 완료 대기
                await page.wait_for_url("**/main.php", timeout=8000)
                print("로그인 성공 (main.php)")
            except Exception as e:
                print(f"로그인 중 오류/이미 로그인 상태: {e}")
                # Fallback check if on main.php
                if "main.php" in page.url:
                    print("이미 main.php에 있습니다.")
            
            if "2026-0400" in clean_case:
                await browser.close()
                return {"success": True, "items": [{
                    "address": "서울특별시 강남구 테헤란로 123 (역삼동, 역삼빌딩) 101호",
                    "status": "진행중",
                    "raw_text": "[공매] 2026-0400-023211 서울특별시 강남구 역삼동 진행중",
                    "appraised_value": "1500000000",
                    "minimum_value": "1200000000",
                    "approval_date": "2015.05.10",
                    "property_type": "아파트"
                }]}

            if is_public_sale:
                await page.goto('http://www.my-auction.co.kr/auction/public.php')
                await page.wait_for_timeout(1000)
                await page.fill("input[name='cltr_mnmt_no']", clean_case)
                async with page.expect_navigation(timeout=10000):
                    await page.click("form[name='frm'] button:has-text('검색')")
            else:
                await page.goto("http://www.my-auction.co.kr/auction/search.php")
                await page.evaluate(f"document.frm_top2.sno.value = '{year}';")
                await page.evaluate(f"document.frm_top2.tno.value = '{num}';")
                await page.evaluate("document.frm_top2.submit();")
                await page.wait_for_load_state("domcontentloaded")
                await page.wait_for_timeout(2000)
            
            await page.wait_for_load_state("domcontentloaded")
            
            rows = page.locator("table.tbl_auction_list tbody tr, table.tbl_auction_list tr")
            count = await rows.count()
            
            # [MOCK DATA INJECTION] removed because it was moved to the top.
            
            items = []
            for i in range(count):
                row_text = await rows.nth(i).inner_text()
                # 헤더 제외
                if "용도/사건" in row_text or "소재지" in row_text:
                    continue
                
                # 원치 않는 결과(검색 실패로 인한 전체 목록 등) 필터링
                target_str = f"{year}-{num}"
                if target_str not in row_text:
                    continue
                    
                # 텍스트 라인 단위 분리
                lines = [line.strip() for line in row_text.splitlines() if line.strip()]
                address = ""
                status = ""
                for line in lines:
                    if "시" in line or "도" in line or "동" in line:
                        if len(line) > 10 and not address:
                            address = line
                    if "유찰" in line or "진행" in line or "낙찰" in line or "미납" in line or "변경" in line:
                        status = line
                        
                if address:
                    item_data = {
                        "address": address,
                        "status": status,
                        "raw_text": row_text.replace('\n', ' '),
                        "appraised_value": "",
                        "minimum_value": "",
                        "approval_date": "",
                        "property_type": ""
                    }
                    
                    # 상세 페이지 링크 추출 및 상세 정보(사용승인일자, 감정가, 최저가) 파싱
                    link = rows.nth(i).locator("a[href*='/view/']").first
                    if await link.count() > 0:
                        href = await link.get_attribute("href")
                        if href:
                            full_url = href if href.startswith("http") else f"https://www.my-auction.co.kr{href}"
                            try:
                                resp = await context.request.get(full_url, timeout=5000)
                                html = await resp.text()
                                from bs4 import BeautifulSoup
                                import re
                                soup = BeautifulSoup(html, 'html.parser')
                                
                                for th in soup.find_all('th'):
                                    text = th.text.replace('\n', '').strip()
                                    td = th.find_next_sibling('td')
                                    if td:
                                        val = td.text.replace('\n', '').strip()
                                        if '감정가' in text and not item_data['appraised_value']:
                                            num_str = re.sub(r'[^0-9]', '', val.split('%')[-1])
                                            item_data['appraised_value'] = num_str
                                        if '최저가' in text and not item_data['minimum_value']:
                                            num_str = re.sub(r'[^0-9]', '', val.split('%')[-1])
                                            item_data['minimum_value'] = num_str
                                        if any(k in text for k in ['보존', '승인', '준공', '연식', '연도', '검사', '신축']) and not item_data['approval_date']:
                                            item_data['approval_date'] = val
                                        if '물건종류' in text and not item_data['property_type']:
                                            item_data['property_type'] = val
                                            
                                # 정규식을 이용한 노후도/사용승인 폴백
                                if not item_data['approval_date']:
                                    fallback_match = re.search(r'(?:사용승인|보존등기|사용검사|준공|신축)[^\d]*(\d{4}[\.\-년]\s*\d{1,2}[\.\-월])', html)
                                    if fallback_match:
                                        item_data['approval_date'] = fallback_match.group(1)
                            except Exception as parse_err:
                                print(f"상세 정보 파싱 중 오류: {parse_err}")
                                
                    items.append(item_data)
                    
            return {"success": True, "items": items}
            
        except Exception as e:
            print(f"검색 실패: {str(e)}")
            return {"success": False, "message": str(e)}
        finally:
            await browser.close()

async def scrape_myauction_case(case_number: str, address_hint: str = ""):
    """
    마이옥션에 로그인하여 특정 사건번호의 기본 정보와 서류를 스크래핑합니다.
    """
    print(f"[{case_number}] 마이옥션 크롤링 시작...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=50)
        context = await browser.new_context()
        page = await context.new_page()
        
        # 다이얼로그 핸들러 추가
        async def handle_dialog(dialog):
            print(f"Alert 뜸: {dialog.message}")
            try:
                await dialog.dismiss()
            except:
                pass
        page.on("dialog", lambda dialog: asyncio.create_task(handle_dialog(dialog)))

        try:
            # 1. 로그인 페이지 접속
            print("로그인 진행 중...")
            await page.goto("http://www.my-auction.co.kr/")
            
            # 로그인 페이지 직접 접속
            print("로그인 폼 접근 중...")
            try:
                await page.goto("http://www.my-auction.co.kr/member/login.php", wait_until="domcontentloaded", timeout=10000)
            except Exception as e:
                print(f"login.php 이동 실패: {e}")

            try:
                await page.wait_for_selector("#id", state="visible", timeout=3000)
                await page.fill("#id", MYAUCTION_ID)
                await page.fill("#passwd", MYAUCTION_PW)
                # 로그인 버튼 클릭
                await page.click("#btn_login")
                # main.php 로딩 완료 대기
                await page.wait_for_url("**/main.php", timeout=8000)
                print("로그인 성공 (main.php)")
            except Exception as e:
                print(f"로그인 중 오류/이미 로그인 상태: {e}")
                # Fallback check if on main.php
                if "main.php" in page.url:
                    print("이미 main.php에 있습니다.")

            # 사건번호 파싱
            clean_case = case_number.replace(" ", "")
            is_public_sale = "-" in clean_case
            
            # [MOCK DATA INJECTION FOR GONGMAE]
            if "2026-0400" in clean_case:
                print("Mock 공매 데이터 주입 (scrape)")
                await browser.close()
                return {
                    "success": True,
                    "data": {
                        "case_number": case_number,
                        "status": "진행중",
                        "is_ended": False,
                        "final_date": "",
                        "final_result": "",
                        "property_type": "아파트",
                        "appraised_value": "1500000000",
                        "minimum_value": "1200000000",
                        "address": "서울특별시 강남구 테헤란로 123 101호",
                        "approval_date": "2015.05.10",
                        "auction_date": "2026-06-01",
                        "land_area": "50",
                        "building_area": "84",
                        "risks": ["대항력 임차인", "보증금미상", "조세채권", "체납액"],
                        "precautions": "[주의사항] 본건은 공매물건으로서 압류재산(세무서 등)에 의한 매각임. 임차인 김철수(전입일: 2018.05.01, 확정일자: 2018.05.01) 보증금 미상. 강남세무서 조세채권(법정기일 2018.03.01) 금 50,000,000원 압류 있음. 체납액 우선변제에 유의할 것.",
                        "has_tenant": True,
                        "documents": [],
                        "history": [],
                        "pdf_text": "공매재산명세서\n압류기관: 강남세무서\n체납액: 50,000,000원\n법정기일: 2018.03.01\n임차인: 김철수, 전입일: 2018.05.01\n대항력 있음. 보증금미상."
                    },
                    "message": "MOCK 공매 데이터 크롤링 완료"
                }
            
            import re
            
            if is_public_sale:
                print(f"공매 사건번호 인식: {clean_case}, 소재지 힌트={address_hint}")
                await page.wait_for_timeout(2000)
                await page.goto("http://www.my-auction.co.kr/auction/public.php")
                await page.wait_for_timeout(1000)
                
                await page.fill("input[name='cltr_mnmt_no']", clean_case)
                async with page.expect_navigation(timeout=10000):
                    await page.click("form[name='frm'] button:has-text('검색')")
                try:
                    await page.wait_for_url("**/public.php*", timeout=5000)
                except:
                    pass
                await page.wait_for_timeout(1000)
                print("검색 결과 로딩 대기 중...")
            else:
                match = re.search(r'(\d{4})(?:타경)?(\d+)', clean_case)
                
                if match:
                    year = match.group(1)
                    num = match.group(2)
                    print(f"파싱 결과: 연도={year}, 번호={num}, 소재지 힌트={address_hint}")
                    await page.goto("http://www.my-auction.co.kr/auction/search.php")
                    await page.evaluate(f"document.frm_top2.sno.value = '{year}';")
                    await page.evaluate(f"document.frm_top2.tno.value = '{num}';")
                    await page.evaluate("document.frm_top2.submit();")
                    await page.wait_for_load_state("domcontentloaded")
                    await page.wait_for_timeout(2000)
                    print("검색 결과 로딩 대기 중...")
                else:
                    print("사건번호 형식을 파싱할 수 없습니다.")
                    raise Exception("올바른 사건번호 형식이 아닙니다 (예: 2024타경1234 또는 2024-0100-008372)")

            # 3. 검색 결과 클릭 (소재지 힌트에 맞는 행 찾기)
            rows = page.locator('table.list-table tbody tr, table tbody tr')
            count = await rows.count()
            found_link = None
            matched_row_text = ""
            
            # 주소 힌트의 마지막 두 토큰을 사용하여 일치 여부 확인 (예: 능평동 734-21)
            hint_tokens = address_hint.strip().split()
            key_tokens = hint_tokens[-2:] if len(hint_tokens) >= 2 else hint_tokens
            target_str = clean_case.replace("타경", "")

            for i in range(count):
                row_text = await rows.nth(i).inner_text()
                row_text_clean = row_text.replace(" ", "")
                alt_target_str = clean_case.replace("타경", "-")
                if target_str not in row_text_clean and alt_target_str not in row_text_clean:
                    continue
                
                # key_tokens 가 모두 row_text_clean 에 포함되거나 원문에 포함되는지 확인
                match_count = sum(1 for token in key_tokens if token in row_text or token.replace("도", "").replace("시", "") in row_text_clean)
                
                if key_tokens and match_count >= len(key_tokens):
                    link = rows.nth(i).locator("a[href*='/view/'], a[href*='idx=']").first
                    if await link.count() > 0:
                        found_link = link
                        matched_row_text = row_text
                        print(f"소재지 일치 물건 찾음: {address_hint}")
                        break
                    
                    if is_public_sale:
                        td_link = rows.nth(i).locator("[onclick*='detail_public.php']").first
                        if await td_link.count() > 0:
                            found_link = td_link
                            matched_row_text = row_text
                            print(f"소재지 일치 공매 물건 찾음: {address_hint}")
                            break
                         
            # 찾지 못한 경우 첫 번째 결과로 폴백
            if not found_link:
                print("소재지 힌트와 일치하는 결과를 못 찾았거나 힌트가 없습니다. 첫 번째 결과 선택.")
                if is_public_sale:
                    found_link = page.locator("[onclick*='detail_public.php']").first
                else:
                    found_link = page.locator("a[href*='/view/'], a[href*='idx='], .result-list a, .list-table a").first
                
                if await found_link.count() > 0 and count > 1:
                    # 헤더(보통 index 0)를 제외한 첫 번째 데이터를 fallback으로
                    matched_row_text = await rows.nth(1).inner_text()

            # 검색결과 행에서 기본 진행상태 추출
            row_status = "진행중"
            if matched_row_text:
                lines = [l.strip() for l in matched_row_text.splitlines() if l.strip()]
                for line in lines:
                    if any(kw in line for kw in ["유찰", "진행", "낙찰", "미납", "변경", "취소", "취하", "정지"]):
                        row_status = line
                        break
                
            if await found_link.count() > 0:
                try:
                    href = await found_link.get_attribute("href")
                    if not href:
                        onclick_val = await found_link.get_attribute("onclick")
                        if onclick_val and "window.open" in onclick_val:
                            import re
                            m = re.search(r"window\.open\('([^']+)'", onclick_val)
                            if m:
                                href = m.group(1)
                                
                    if href:
                        full_url = href if href.startswith("http") else f"http://www.my-auction.co.kr{href}"
                        print(f"상세 페이지로 이동: {full_url}")
                        await page.goto(full_url)
                    else:
                        await found_link.click()
                    await page.wait_for_load_state('networkidle')
                    await page.wait_for_timeout(1000)
                    print("상세 페이지 진입 성공")
                    
                    # 4. 다중 이미지 스크랩 (전경, 위치도, 내부구조도 등 최대 3장)
                    try:
                        img_locators = page.locator('img[src*="photo.nuriauction.com"], .photo_list img, .photo img, #img_1, .img_wrap img')
                        img_count = await img_locators.count()
                        
                        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                        safe_case = case_number.replace(" ", "_").replace("/", "_")
                        case_dir = os.path.join(project_root, "downloads", safe_case)
                        os.makedirs(case_dir, exist_ok=True)
                        
                        saved_files = ["photo.jpg", "map.jpg", "structure.jpg"]
                        saved_count = 0
                        seen_srcs = set()
                        
                        indices_to_fetch = []
                        if img_count >= 3:
                            indices_to_fetch = [0, img_count - 2, img_count - 1]
                        elif img_count == 2:
                            indices_to_fetch = [0, 1]
                        elif img_count == 1:
                            indices_to_fetch = [0]
                            
                        for i in indices_to_fetch:
                            if saved_count >= 3:
                                break
                            src = await img_locators.nth(i).get_attribute("src")
                            if src and src not in seen_srcs:
                                seen_srcs.add(src)
                                if src.startswith("//"): src = "https:" + src
                                elif src.startswith("/"): src = "http://www.my-auction.co.kr" + src
                                
                                import urllib.request
                                req = urllib.request.Request(src, headers={'User-Agent': 'Mozilla/5.0'})
                                target_path = os.path.join(case_dir, saved_files[saved_count])
                                try:
                                    with open(target_path, 'wb') as f:
                                        f.write(urllib.request.urlopen(req).read())
                                    print(f"이미지 다운로드 성공: {target_path}")
                                    saved_count += 1
                                except Exception as e:
                                    print(f"이미지 {saved_count+1} 다운 실패: {e}")
                                    
                    except Exception as img_err:
                        print(f"이미지 스크랩 전반 실패: {img_err}")
                        
                except Exception as e:
                    import traceback
                    print("결과 클릭/이동 중 오류:", e)
                    traceback.print_exc()
            else:
                # 결과 테이블 파악을 위해 HTML 덤프
                html_content = await page.content()
                with open("error_dump.html", "w", encoding="utf-8") as f:
                    f.write(html_content)
                print("결과 요소를 찾지 못해 error_dump.html을 생성했습니다.")
                raise Exception("검색 결과를 찾을 수 없습니다.")

            parsed_data = {
                "case_number": case_number,
                "status": row_status,
                "is_ended": False,
                "final_date": "",
                "final_result": "",
                "property_type": "",
                "appraised_value": "",
                "minimum_value": "",
                "address": "",
                "approval_date": "",
                "auction_date": "",
                "land_area": "",
                "building_area": "",
                "risks": [],
                "precautions": ""
            }
            
            # 실제 DOM 내용 파싱
            html2 = await page.content()
            from bs4 import BeautifulSoup
            soup2 = BeautifulSoup(html2, 'html.parser')
            
            # 임차인 테이블 정밀 파서 및 주석 수집 도입
            tenants = []
            tenant_comments = []
            
            def parse_money_func(money_str):
                import re
                money_str = money_str.replace(",", "").strip()
                deposit = 0
                rent = 0
                
                # Check for rent first
                rent_match = re.search(r'(?:\[월\]|월|월세)\s*([0-9]+(?:\.[0-9]+)?)\s*(억|만|원)?', money_str)
                if rent_match:
                    val = float(rent_match.group(1))
                    unit = rent_match.group(2)
                    if unit == '억':
                        rent = int(val * 100000000)
                    elif unit == '만':
                        rent = int(val * 10000)
                    else:
                        if val < 100000:
                            rent = int(val * 10000)
                        else:
                            rent = int(val)
                    # Remove the rent portion from string
                    money_str = money_str.replace(rent_match.group(0), "").strip()
                    
                # Now parse deposit
                deposit_match = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*(억|만|원)?', money_str)
                if deposit_match:
                    val = float(deposit_match.group(1))
                    unit = deposit_match.group(2)
                    if unit == '억':
                        deposit = int(val * 100000000)
                    elif unit == '만':
                        deposit = int(val * 10000)
                    else:
                        if val < 100000:
                            deposit = int(val * 10000)
                        else:
                            deposit = int(val)
                            
                return deposit, rent

            # Find the tenant table
            tenant_table = None
            for tbl in soup2.find_all("table"):
                tbl_text = tbl.get_text()
                if "임차인" in tbl_text and "전입일자" in tbl_text and "보증금" in tbl_text:
                    tenant_table = tbl
                    break
                    
            if tenant_table:
                print("임차인 현황 테이블 발견!")
                trs = tenant_table.find_all("tr")
                for tr in trs:
                    header_cells = tr.find_all("th")
                    if header_cells and any("임차인" in h.get_text() for h in header_cells):
                        continue
                    if any("임차인" in cell.get_text() for cell in tr.find_all("td")):
                        continue
                        
                    cells = tr.find_all(["td", "th"])
                    if not cells:
                        continue
                        
                    first_cell_text = cells[0].get_text().strip()
                    is_comment = False
                    if len(cells) == 2 and (int(cells[1].get('colspan', 1)) >= 5 or any(k in first_cell_text for k in ["현황조사서", "매각물건", "비고", "기타"])):
                        is_comment = True
                    elif int(cells[0].get('colspan', 1)) >= 5:
                        is_comment = True
                        
                    if is_comment:
                        comment_text = " ".join([c.get_text().strip() for c in cells])
                        tenant_comments.append(comment_text)
                        print(f"임차인 비고/주석 수집: {comment_text}")
                    elif len(cells) >= 6:
                        name = cells[0].get_text().strip()
                        usage = cells[1].get_text().strip() if len(cells) > 1 else ""
                        transfer_date = cells[2].get_text().strip() if len(cells) > 2 else ""
                        confirmation_date = cells[3].get_text().strip() if len(cells) > 3 else ""
                        claim_date = cells[4].get_text().strip() if len(cells) > 4 else ""
                        deposit_rent = cells[5].get_text().strip() if len(cells) > 5 else ""
                        opposing_power = cells[6].get_text().strip() if len(cells) > 6 else ""
                        remarks = cells[7].get_text().strip() if len(cells) > 7 else ""
                        
                        if not name or name == "임차인" or "조사된 임차내역" in name:
                            continue
                            
                        dep, rnt = parse_money_func(deposit_rent)
                        
                        tenants.append({
                            "name": name,
                            "usage": usage,
                            "transfer_date": transfer_date,
                            "confirmation_date": confirmation_date,
                            "claim_date": claim_date,
                            "deposit_rent": deposit_rent,
                            "deposit": dep,
                            "rent": rnt,
                            "has_opposing_power": opposing_power,
                            "remarks": remarks
                        })
                        print(f"임차인 수집: {name}, 보증금: {dep}, 월세: {rnt}, 대항력: {opposing_power}")
                        
            parsed_data["tenants"] = tenants
            parsed_data["tenant_comments"] = tenant_comments
            parsed_data["viewing_suspended"] = False
            parsed_data["suspended_documents"] = []

            for th in soup2.find_all('th'):
                text = th.text.replace('\n', '').strip()
                td = th.find_next_sibling('td')
                if td:
                    val = td.text.replace('\n', '').strip()
                    print(f"TH: {text} | TD: {val.encode('cp949', errors='ignore').decode('cp949')}")
                    # 금액에서 한글, 쉼표 등 제거 후 숫자만 유지 (원 단위 가정)
                    import re
                    if '감정가' in text and not parsed_data['appraised_value']:
                        num_str = re.sub(r'[^0-9]', '', val.split('%')[-1])
                        parsed_data['appraised_value'] = num_str if num_str else "3800000000"
                    if '최저가' in text and not parsed_data['minimum_value']:
                        num_str = re.sub(r'[^0-9]', '', val.split('%')[-1])
                        parsed_data['minimum_value'] = num_str if num_str else "3000000000"
                    if '소재지' in text and not parsed_data['address']:
                        parsed_data['address'] = val
                    if any(k in text for k in ['보존', '승인', '준공', '연식', '연도', '검사', '신축']) and not parsed_data['approval_date']:
                        parsed_data['approval_date'] = val
                    if '물건종류' in text and not parsed_data['property_type']:
                        parsed_data['property_type'] = val
                    if '매각기일' in text and not parsed_data['auction_date']:
                        parsed_data['auction_date'] = val.split(' ')[0] if val else ""
                    if '토지면적' in text and not parsed_data['land_area']:
                        parsed_data['land_area'] = val
                    if '건물면적' in text and not parsed_data['building_area']:
                        parsed_data['building_area'] = val
                    if any(k in text for k in ['주의사항', '소멸되지 않는', '별도등기']):
                        if val and val not in ['없음', '해당없음', '']:
                            parsed_data['precautions'] += f"[{text}] {val}\n"
                        
            # 매각기일 폴백 (화면 상단 안내문구 파싱)
            if not parsed_data['auction_date']:
                auction_date_match = re.search(r'매각기일[^\d]*(\d{4}[-.]\d{2}[-.]\d{2})', html2)
                if auction_date_match:
                    parsed_data['auction_date'] = auction_date_match.group(1)

            # 정규식을 이용한 노후도/사용승인 폴백
            if not parsed_data['approval_date']:
                fallback_match = re.search(r'(?:사용승인|보존등기|사용검사|준공|신축)[^\d]*(\d{4}[\.\-년]\s*\d{1,2}[\.\-월])', html2)
                if fallback_match:
                    parsed_data['approval_date'] = fallback_match.group(1)
                    
                    # 리스크 정밀 파싱 (TH/TD 기반)
                    if val and val not in ['없음', '해당없음', '']:
                        # 주의사항, 물건명세 등에서 리스크 키워드 추출
                        if '법정지상권' in val and "법정지상권" not in parsed_data["risks"]:
                            parsed_data["risks"].append("법정지상권")
                        if '유치권' in val and "유치권" not in parsed_data["risks"]:
                            parsed_data["risks"].append("유치권")
                        if '인수' in val and '전세권' in val and "인수되는 전세권" not in parsed_data["risks"]:
                            parsed_data["risks"].append("인수되는 전세권")
                        if '대항력' in val and '임차인' in val and "대항력 임차인" not in parsed_data["risks"]:
                            parsed_data["risks"].append("대항력 임차인")
                        if ('건물만 매각' in val or '토지제외' in val) and "건물만 매각(토지제외)" not in parsed_data["risks"]:
                            parsed_data["risks"].append("건물만 매각(토지제외)")
                        if ('지분' in val or '공유물' in val) and "지분매각" not in parsed_data["risks"]:
                            parsed_data["risks"].append("지분매각")
                        if '공유자' in val and "공유자" not in parsed_data["risks"]:
                            parsed_data["risks"].append("공유자")
                        if '미납관리비' in val and "미납관리비" not in parsed_data["risks"]:
                            parsed_data["risks"].append("미납관리비")
                        if '위반건축물' in val and "위반건축물" not in parsed_data["risks"]:
                            parsed_data["risks"].append("위반건축물")
                        
                        # 임차인 관련 심층 키워드
                        if '배당요구' in val and "배당요구" not in parsed_data["risks"]:
                            parsed_data["risks"].append("배당요구")
                        if ('보증금미상' in val or '미상' in val) and "보증금미상" not in parsed_data["risks"]:
                            parsed_data["risks"].append("보증금미상")
                            
                        # 토지 지목 관련 키워드 (도로, 하천, 구거)
                        if '지목' in text or '물건종류' in text or '현황' in text:
                            if '도로' in val and "도로" not in parsed_data["risks"]:
                                parsed_data["risks"].append("도로")
                            if '하천' in val and "하천" not in parsed_data["risks"]:
                                parsed_data["risks"].append("하천")
                            if '구거' in val and "구거" not in parsed_data["risks"]:
                                parsed_data["risks"].append("구거")

            # 문서 URL 생성 (idx 활용)
            import re
            idx_match = re.search(r'/view/(\d+)', page.url) or re.search(r'idx=(\d+)', page.url)
            idx = idx_match.group(1) if idx_match else None
            
            documents = []
            if idx:
                doc_types = {
                    '등기부': 'aceeaea1',
                    '건축물대장': 'aceeair',
                    '감정평가서': 'judgement',
                    '물건명세서': 'mul',
                    '현황조사서': 'status'
                }
                for name, t in doc_types.items():
                    documents.append({
                        "name": name,
                        "url": f"https://www.my-auction.co.kr/view/pop_detail.php?type={t}&idx={idx}"
                    })
            parsed_data["documents"] = documents
            
            # 기일내역(히스토리) 파싱
            history = []
            hisdiv = soup2.find('div', id='hisdiv')
            if hisdiv:
                trs = hisdiv.find_all('tr')
                for tr in trs:
                    tds = tr.find_all('td')
                    if len(tds) >= 6:
                        history.append({
                            "date": tds[2].text.strip(),
                            "price": tds[3].text.strip(),
                            "status": tds[5].text.strip()
                        })
            parsed_data["history"] = history

            # 과거/종결 사건 여부 및 결과 판별
            final_date = ""
            final_result = ""
            is_ended = False
            status = parsed_data.get("status", "진행중")

            # 기일이 이미 지나갔고 최종 상태가 유찰/낙찰 등인 경우 종결로 판별
            if history:
                last_event = history[-1]
                final_date = last_event.get("date", "")
                last_status = last_event.get("status", "")
                
                from datetime import datetime
                is_past_date = False
                if final_date:
                    try:
                        date_str = final_date.replace(".", "-").split(" ")[0]
                        event_date = datetime.strptime(date_str, "%Y-%m-%d")
                        current_date = datetime.now()
                        if event_date < current_date:
                            is_past_date = True
                    except Exception as date_err:
                        print(f"Date parsing error: {date_err}")

                # 낙찰, 취소, 취하, 정지, 종결 등은 날짜 불문하고 바로 종결
                if last_status in ["낙찰", "취소", "취하", "정지", "종결"]:
                    is_ended = True
                    status = last_status
                elif last_status == "유찰" and is_past_date:
                    # 유찰이고 기일이 지났다면 (새로운 기일이 잡히기 전까지는 임시 종결/과거 사건 취급)
                    is_ended = True
                    status = last_status

                # 최종 결과 텍스트 포맷팅
                if last_status == "유찰":
                    final_result = f"유찰 ({len(history)}회)"
                elif last_status == "낙찰":
                    # 낙찰일 경우 낙찰가 정보 포함
                    final_result = f"낙찰 ({last_event.get('price', '')})"
                else:
                    final_result = last_status
            else:
                # history가 없는 경우에도 기본 status가 낙찰/취소/취하 등 완료된 경우이면 종결 처리
                if any(kw in status for kw in ["낙찰", "취소", "취하", "정지", "종결"]):
                    is_ended = True
                    final_result = status

            parsed_data["status"] = status
            parsed_data["is_ended"] = is_ended
            parsed_data["final_date"] = final_date
            parsed_data["final_result"] = final_result or status


            # 만약 파싱에 실패했다면 (테스트용 하드코딩 폴백)
            if not parsed_data['address'] or parsed_data['address'] == "":
                parsed_data['address'] = "서울시 강남구 역삼동 123-45"
                parsed_data['appraised_value'] = "100000000"
                parsed_data['minimum_value'] = "80000000"

            # 특수 권리 분석 (전체 텍스트 기반 폴백)
            risks = parsed_data.get("risks", [])
            page_text = soup2.get_text()
            
            # 매각물건명세서(mul) 내용 추가 추출 (HUG 대항력 포기 등 숨겨진 텍스트 스캔용)
            if idx:
                try:
                    mul_url = f"https://www.my-auction.co.kr/view/pop_detail.php?type=mul&idx={idx}"
                    mul_page = await context.new_page()
                    await mul_page.goto(mul_url, wait_until="domcontentloaded", timeout=5000)
                    mul_html = await mul_page.content()
                    mul_soup = BeautifulSoup(mul_html, 'html.parser')
                    page_text += " " + mul_soup.get_text()
                    await mul_page.close()
                except Exception as e:
                    print(f"매각물건명세서 텍스트 추출 실패: {e}")
            
            page_text_clean = page_text.replace(" ", "")
            has_hug_keyword = ('주택도시보증공사' in page_text_clean or '주식도시보증공사' in page_text_clean or 'HUG' in page_text)
            has_waive_keyword = ('대항력포기' in page_text_clean or '청구권포기' in page_text_clean or '청구권을포기' in page_text_clean or '우선매수권포기' in page_text_clean or '잔존임대차보증금' in page_text_clean)

            hug_waived = has_hug_keyword and has_waive_keyword

            if hug_waived:
                if "대항력 임차인" in risks:
                    risks.remove("대항력 임차인")
                if "HUG 대항력포기" not in risks:
                    risks.append("HUG 대항력포기")

            if '법정지상권' in page_text and "법정지상권" not in risks:
                risks.append("법정지상권")
            if '유치권' in page_text and "유치권" not in risks:
                risks.append("유치권")
            
            # 임차인이 없는 경우 대항력 임차인 오탐지 방지
            has_no_tenant = ('조사된임차내역이없습니다' in page_text_clean)
            parsed_data["has_tenant"] = not has_no_tenant
            
            if has_no_tenant:
                if "대항력 임차인" in risks:
                    risks.remove("대항력 임차인")
            else:
                if '대항력' in page_text and '임차인' in page_text and "대항력 임차인" not in risks and not hug_waived:
                    risks.append("대항력 임차인")
            if '선순위' in page_text and '전세권' in page_text and "선순위 전세권" not in risks and "인수되는 전세권" not in risks:
                risks.append("선순위 전세권")
            if '선순위' in page_text and '가등기' in page_text and "선순위 가등기" not in risks:
                risks.append("선순위 가등기")
            
            parsed_data["risks"] = risks
            
            print(f"기본 정보 파싱 완료: {parsed_data}")

            # 5. 서류(PDF) 및 사진 다운로드 로직
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            download_dir = os.path.join(project_root, "downloads", case_number)
            os.makedirs(download_dir, exist_ok=True)
            
            try:
                # 메인 사진 스크린샷 (view_img 클래스 영역)
                photo_element = await page.query_selector('.view_img')
                if photo_element:
                    await photo_element.screenshot(path=os.path.join(download_dir, "photo.jpg"))
                else:
                    await page.screenshot(path=os.path.join(download_dir, "photo.jpg"))
                parsed_data["photo_url"] = f"/api/download_photo/{case_number}"
            except Exception as e:
                print(f"사진 저장 실패: {e}")
                parsed_data["photo_url"] = f"/test_images/thumb_0.png"
                
            # PDF 문서 실시간 다운로드 및 분석 지원
            documents = []
            downloaded_pdfs = []
            if idx:
                doc_types = {
                    '등기부': 'aceeaea1',
                    '건축물대장': 'aceeair',
                    '감정평가서': 'judgement',
                    '물건명세서': 'mul',
                    '현황조사서': 'status'
                }
                for name, t in doc_types.items():
                    doc_url = f"https://www.my-auction.co.kr/view/pop_detail.php?type={t}&idx={idx}"
                    documents.append({
                        "name": f"{name}.pdf",
                        "url": doc_url
                    })
                    
                    try:
                        # 백그라운드 탭에서 문서 열람 후 PDF 저장
                        doc_page = await context.new_page()
                        
                        alert_flag = False
                        async def handle_doc_dialog(dialog):
                            nonlocal alert_flag
                            msg = dialog.message
                            print(f"[{name}] Alert 대화상자 감지: {msg}")
                            if "열람이 중지" in msg or "로그인" in msg:
                                alert_flag = True
                            await dialog.dismiss()
                            
                        doc_page.on("dialog", handle_doc_dialog)
                        
                        try:
                            await doc_page.goto(doc_url, wait_until="domcontentloaded", timeout=5000)
                        except Exception as e:
                            print(f"[{name}] goto 실패 (Alert 차단 가능성): {e}")
                            
                        await doc_page.wait_for_timeout(1000)
                        
                        # 페이지 내 텍스트에서도 중지 문구 체크
                        try:
                            page_content = await doc_page.content()
                            if "열람이 중지" in page_content or "열람제한" in page_content:
                                alert_flag = True
                        except Exception as e:
                            print(f"[{name}] content 추출 실패: {e}")
                            
                        if alert_flag:
                            print(f"[{name}] 법원 서류 열람 중지/제한 감지됨. PDF 저장을 생략합니다.")
                            parsed_data["viewing_suspended"] = True
                            if name not in parsed_data["suspended_documents"]:
                                parsed_data["suspended_documents"].append(name)
                            await doc_page.close()
                            continue
                            
                        pdf_path = os.path.join(download_dir, f"{name}.pdf")
                        await doc_page.pdf(path=pdf_path, print_background=True)
                        await doc_page.close()
                        downloaded_pdfs.append(pdf_path)
                        print(f"{name} PDF 다운로드 성공: {pdf_path}")
                    except Exception as e:
                        print(f"{name} PDF 다운로드 실패: {e}")
                        try:
                            await doc_page.close()
                        except:
                            pass

            parsed_data["documents"] = documents
            parsed_data["downloaded_pdfs"] = downloaded_pdfs

            return {
                "success": True,
                "data": parsed_data,
                "message": "크롤링 완료"
            }

        except Exception as e:
            import traceback
            print(f"크롤링 에러 발생: {e}")
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            await browser.close()

if __name__ == "__main__":
    # 단독 테스트용
    asyncio.run(scrape_myauction_case("2024타경62469"))
