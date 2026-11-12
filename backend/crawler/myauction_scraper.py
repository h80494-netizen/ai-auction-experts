# -*- coding: utf-8 -*-
import os
import re
import base64
import sqlite3
import asyncio
import urllib.request
from datetime import datetime
from typing import Dict, Any, List, Optional

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_root = os.path.dirname(backend_dir)

for candidate_env in [os.path.join(backend_dir, ".env"), os.path.join(project_root, ".env")]:
    if os.path.exists(candidate_env):
        load_dotenv(dotenv_path=candidate_env, override=False)

MYAUCTION_ID = os.getenv("MYAUCTION_ID", "")
MYAUCTION_PW = os.getenv("MYAUCTION_PW", "")
MYAUCTION_BASE = "https://www.my-auction.co.kr"


def _create_logged_in_session() -> requests.Session:
    """
    마이옥션 고속 HTTP 로그인 세션 생성 (Playwright 기동 없이 0.1초 내 쿠키 획득).
    """
    sess = requests.Session()
    sess.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8",
        "Referer": f"{MYAUCTION_BASE}/member/login.php",
    })
    if MYAUCTION_ID and MYAUCTION_PW:
        try:
            b_id = base64.b64encode(MYAUCTION_ID.encode("utf-8")).decode("ascii")
            b_pw = base64.b64encode(MYAUCTION_PW.encode("utf-8")).decode("ascii")
            sess.post(
                f"{MYAUCTION_BASE}/member/login_handle.php",
                data={
                    "rtn_page": "",
                    "id": b_id,
                    "pwd": b_pw,
                    "login_id": "",
                    "login_pw": "",
                    "loging": "Y",
                },
                timeout=(5, 8),
            )
        except Exception as e:
            print(f"[MyAuction HTTP] 로그인 요청 경고 (비로그인 조회 계속): {e}")
    return sess


def parse_case_components(case_number: str) -> Dict[str, Any]:
    """
    사건번호 문자열에서 연도, 번호, 괄호 물건번호((1), [1], 물건1 등), 관할법원 힌트, 공매 여부를 정밀 파싱합니다.
    예: '서울서부 2025 타경 51673(1)' -> year='2025', num='51673', item_no='1', court_hint='서울서부', is_public_sale=False
    """
    raw = (case_number or "").strip()
    normalized = raw.replace("（", "(").replace("）", ")").replace("[", "(").replace("]", ")")
    clean = re.sub(r"\s+", "", normalized)

    is_public_sale = bool(re.search(r"\d{4}-\d{3,5}-\d{4,}", clean)) or (clean.count("-") >= 2 and "타경" not in clean)
    if is_public_sale:
        return {
            "raw": raw,
            "clean": clean,
            "is_public_sale": True,
            "year": "",
            "num": "",
            "item_no": "",
            "court_hint": "",
            "has_parenthesis": False,
        }

    item_no = ""
    m_paren = re.search(r"\((\d+)\)\s*$", clean) or re.search(r"(?:물건번호?|호수?)(\d+)\s*$", clean)
    if m_paren:
        item_no = str(int(m_paren.group(1)))

    m_case = re.search(r"(\d{4})(?:타경|-)?(\d+)", clean)
    year = m_case.group(1) if m_case else ""
    num = str(int(m_case.group(2))) if m_case else ""

    if not item_no and m_case:
        tail = clean[m_case.end():]
        m_tail = re.match(r"^[-_](\d+)$", tail)
        if m_tail:
            item_no = str(int(m_tail.group(1)))

    court_hint = ""
    if m_case and m_case.start() > 0:
        prefix = re.sub(r"[^가-힣]", "", clean[:m_case.start()])
        if prefix:
            court_hint = prefix.replace("지방법원", "").replace("지원", "").replace("법원", "")

    has_paren = ("(" in normalized and ")" in normalized) or bool(item_no)
    return {
        "raw": raw,
        "clean": clean,
        "is_public_sale": False,
        "year": year,
        "num": num,
        "item_no": item_no,
        "court_hint": court_hint,
        "has_parenthesis": has_paren,
    }


def _lookup_local_auctions_db(case_number: str, address_hint: str = "") -> List[Dict[str, Any]]:
    """
    마이옥션 지연/점검 또는 미검색 시 로컬 map_data.db(auctions 테이블)에서 물건번호((1) 등)까지 정밀 대조합니다.
    """
    db_candidates = [
        os.path.join(backend_dir, "data", "map_data.db"),
        os.path.join(project_root, "data", "map_data.db"),
    ]
    db_path = next((p for p in db_candidates if os.path.exists(p)), None)
    if not db_path:
        return []

    comp = parse_case_components(case_number)
    year, num, req_item_no = comp["year"], comp["num"], comp["item_no"]
    patterns = [case_number.strip()]
    if year and num:
        base_forms = [f"{year} 타경 {num}", f"{year}타경{num}", f"{year}-{num}"]
        if req_item_no:
            for bf in base_forms:
                patterns.append(f"{bf}({req_item_no})")
        patterns.extend(base_forms)

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        rows = []
        if year and num:
            cur.execute(
                "SELECT * FROM auctions WHERE REPLACE(case_no, ' ', '') LIKE ? LIMIT 25",
                (f"%{year}%{num}%",),
            )
            rows = cur.fetchall()
        if not rows:
            placeholders = ",".join(["?"] * len(patterns))
            cur.execute(f"SELECT * FROM auctions WHERE case_no IN ({placeholders})", patterns)
            rows = cur.fetchall()
        conn.close()
    except Exception as e:
        print(f"[LocalDB Fallback] 조회 오류: {e}")
        return []

    hint_tokens = [t for t in re.split(r"[\s,]+", (address_hint or "").strip()) if len(t) >= 2]
    results = []
    for r in rows:
        d = dict(r)
        c_raw = str(d.get("case_no") or case_number).strip()
        row_comp = parse_case_components(c_raw)
        if year and num and (row_comp["year"] != year or row_comp["num"] != num):
            continue
        row_item = row_comp["item_no"]
        appr = int(float(d.get("appraisal_price") or 0))
        minp = int(float(d.get("min_price") or 0))
        area_py = float(d.get("area_size") or 0.0)
        land_py = float(d.get("land_size") or 0.0)
        b_area_str = f"{area_py * 3.3058:.2f} ㎡ ({area_py:.2f}평)" if area_py > 0 else ""
        l_area_str = f"{land_py * 3.3058:.2f} ㎡ ({land_py:.2f}평)" if land_py > 0 else ""
        addr_val = d.get("address") or ""

        score = 0
        if req_item_no:
            score += 1000 if row_item == req_item_no else -500
        score += sum(50 for tok in hint_tokens if tok in addr_val)

        results.append({
            "case_no": c_raw,
            "case_no_full": c_raw,
            "item_no": row_item,
            "court": "",
            "myauction_idx": "",
            "exact_item_match": bool(req_item_no and row_item == req_item_no),
            "_score": score,
            "address": addr_val,
            "status": "진행중",
            "raw_text": f"[DB] {c_raw} {addr_val} {d.get('special_notes') or ''}",
            "appraised_value": str(appr) if appr > 0 else "",
            "minimum_value": str(minp) if minp > 0 else "",
            "approval_date": "",
            "property_type": d.get("property_type") or "부동산",
            "building_area": b_area_str,
            "land_area": l_area_str,
            "pyeong": round(area_py, 2) if area_py > 0 else 0.0,
            "sale_date": d.get("sale_date") or "",
            "special_notes": d.get("special_notes") or "",
            "official_land_price": d.get("official_land_price") or 0,
            "lat": d.get("lat"),
            "lng": d.get("lng"),
        })

    results.sort(key=lambda x: (-x.get("_score", 0), int(x["item_no"]) if str(x.get("item_no", "")).isdigit() else 999))
    for item in results:
        item.pop("_score", None)
    return results


def _parse_money_func(money_str: str):
    money_str = (money_str or "").replace(",", "").strip()
    deposit = 0
    rent = 0

    rent_match = re.search(r"(?:\[월\]|월|월세)\s*([0-9]+(?:\.[0-9]+)?)\s*(억|만|원)?", money_str)
    if rent_match:
        val = float(rent_match.group(1))
        unit = rent_match.group(2)
        if unit == "억":
            rent = int(val * 100000000)
        elif unit == "만":
            rent = int(val * 10000)
        else:
            rent = int(val * 10000) if val < 100000 else int(val)
        money_str = money_str.replace(rent_match.group(0), "").strip()

    deposit_match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*(억|만|원)?", money_str)
    if deposit_match:
        val = float(deposit_match.group(1))
        unit = deposit_match.group(2)
        if unit == "억":
            deposit = int(val * 100000000)
        elif unit == "만":
            deposit = int(val * 10000)
        else:
            deposit = int(val * 10000) if val < 100000 else int(val)

    return deposit, rent


def _parse_detail_html(
    soup2: BeautifulSoup,
    html2: str,
    case_number: str,
    row_status: str,
    idx: Optional[str],
    sess: Optional[requests.Session] = None,
) -> Dict[str, Any]:
    """마이옥션 상세 페이지 HTML을 정밀 파싱하여 표준 데이터 구조로 반환합니다."""
    parsed_data: Dict[str, Any] = {
        "case_number": case_number,
        "status": row_status or "진행중",
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
        "precautions": "",
        "tenants": [],
        "tenant_comments": [],
        "viewing_suspended": False,
        "suspended_documents": [],
        "documents": [],
        "history": [],
        "scraped_doc_text": "",
    }

    tenants = []
    tenant_comments = []

    tenant_table = None
    for tbl in soup2.find_all("table"):
        tbl_text = tbl.get_text()
        if "임차인" in tbl_text and "전입일자" in tbl_text and "보증금" in tbl_text:
            tenant_table = tbl
            break

    if tenant_table:
        for tr in tenant_table.find_all("tr"):
            header_cells = tr.find_all("th")
            if header_cells and any("임차인" in h.get_text() for h in header_cells):
                continue
            if any(cell.get_text().strip() == "임차인" for cell in tr.find_all("td")):
                continue

            cells = tr.find_all(["td", "th"])
            if not cells:
                continue

            first_cell_text = cells[0].get_text().strip()
            colspan0 = int(cells[0].get("colspan", 1) or 1)
            colspan1 = int(cells[1].get("colspan", 1) or 1) if len(cells) > 1 else 1
            is_comment = False
            if len(cells) == 2 and (colspan1 >= 5 or any(k in first_cell_text for k in ["현황조사서", "매각물건", "비고", "기타"])):
                is_comment = True
            elif colspan0 >= 5:
                is_comment = True

            if is_comment:
                comment_text = " ".join([c.get_text(" ", strip=True) for c in cells])
                tenant_comments.append(comment_text)
            elif len(cells) >= 6:
                name = cells[0].get_text(strip=True)
                usage = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                transfer_date = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                confirmation_date = cells[3].get_text(strip=True) if len(cells) > 3 else ""
                claim_date = cells[4].get_text(strip=True) if len(cells) > 4 else ""
                deposit_rent = cells[5].get_text(strip=True) if len(cells) > 5 else ""
                opposing_power = cells[6].get_text(strip=True) if len(cells) > 6 else ""
                remarks = cells[7].get_text(strip=True) if len(cells) > 7 else ""

                if not name or name == "임차인" or "조사된 임차내역" in name:
                    continue

                dep, rnt = _parse_money_func(deposit_rent)
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
                    "remarks": remarks,
                })

    parsed_data["tenants"] = tenants
    parsed_data["tenant_comments"] = tenant_comments

    for th in soup2.find_all("th"):
        text = th.get_text(" ", strip=True)
        td = th.find_next_sibling("td")
        if not td:
            continue
        val = td.get_text(" ", strip=True)
        if "감정가" in text and not parsed_data["appraised_value"]:
            num_str = re.sub(r"[^0-9]", "", val.split("%")[-1])
            if num_str:
                parsed_data["appraised_value"] = num_str
        if "최저가" in text and not parsed_data["minimum_value"]:
            num_str = re.sub(r"[^0-9]", "", val.split("%")[-1])
            if num_str:
                parsed_data["minimum_value"] = num_str
        if "소재지" in text and not parsed_data["address"]:
            parsed_data["address"] = val
        if any(k in text for k in ["보존", "승인", "준공", "연식", "연도", "검사", "신축"]) and not parsed_data["approval_date"]:
            parsed_data["approval_date"] = val
        if "물건종류" in text and not parsed_data["property_type"]:
            parsed_data["property_type"] = val
        if "매각기일" in text and not parsed_data["auction_date"]:
            parsed_data["auction_date"] = val.split(" ")[0] if val else ""
        if "토지면적" in text and not parsed_data["land_area"]:
            parsed_data["land_area"] = val
        if "건물면적" in text and not parsed_data["building_area"]:
            parsed_data["building_area"] = val
        if any(k in text for k in ["주의사항", "소멸되지 않는", "별도등기", "매각물건", "명세서비고", "특기사항"]):
            if val and val not in ["없음", "해당없음", ""]:
                header_clean = re.sub(r"\s+", " ", text).strip()
                parsed_data["precautions"] += f"[{header_clean}] {val}\n"

        if val and val not in ["없음", "해당없음", ""]:
            risk_pairs = [
                ("법정지상권", "법정지상권"),
                ("유치권", "유치권"),
                ("미납관리비", "미납관리비"),
                ("위반건축물", "위반건축물"),
                ("배당요구", "배당요구"),
            ]
            for kw, label in risk_pairs:
                if kw in val and label not in parsed_data["risks"]:
                    parsed_data["risks"].append(label)
            if "인수" in val and "전세권" in val and "인수되는 전세권" not in parsed_data["risks"]:
                parsed_data["risks"].append("인수되는 전세권")
            if "대항력" in val and "임차인" in val and "대항력 임차인" not in parsed_data["risks"]:
                parsed_data["risks"].append("대항력 임차인")
            if ("건물만 매각" in val or "토지제외" in val) and "건물만 매각(토지제외)" not in parsed_data["risks"]:
                parsed_data["risks"].append("건물만 매각(토지제외)")
            if ("지분" in val or "공유물" in val) and "지분매각" not in parsed_data["risks"]:
                parsed_data["risks"].append("지분매각")
            if ("보증금미상" in val or "미상" in val) and "보증금미상" not in parsed_data["risks"]:
                parsed_data["risks"].append("보증금미상")

    if not parsed_data["auction_date"]:
        auction_date_match = re.search(r"매각기일[^\d]*(\d{4}[-.]\d{2}[-.]\d{2})", html2)
        if auction_date_match:
            parsed_data["auction_date"] = auction_date_match.group(1)

    if not parsed_data["approval_date"]:
        fallback_match = re.search(
            r"(?:사용승인|보존등기|사용검사|준공|신축)[^\d]*(\d{4}[\.\-년]\s*\d{1,2}[\.\-월](?:\s*\d{1,2}[일]?)?)",
            html2,
        )
        if fallback_match:
            parsed_data["approval_date"] = fallback_match.group(1).strip()

    history = []
    hisdiv = soup2.find("div", id="hisdiv")
    if hisdiv:
        for tr in hisdiv.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) >= 6:
                history.append({
                    "date": tds[2].get_text(strip=True),
                    "price": tds[3].get_text(strip=True),
                    "status": tds[5].get_text(strip=True),
                })
    parsed_data["history"] = history

    final_date = ""
    final_result = ""
    is_ended = False
    status = parsed_data.get("status", "진행중")

    if history:
        last_event = history[-1]
        final_date = last_event.get("date", "")
        last_status = last_event.get("status", "")
        is_past_date = False
        if final_date:
            try:
                date_str = final_date.replace(".", "-").split(" ")[0]
                event_date = datetime.strptime(date_str, "%Y-%m-%d")
                if event_date < datetime.now():
                    is_past_date = True
            except Exception:
                pass
        if last_status in ["낙찰", "취소", "취하", "정지", "종결"]:
            is_ended = True
            status = last_status
        elif last_status == "유찰" and is_past_date:
            is_ended = True
            status = last_status

        if last_status == "유찰":
            final_result = f"유찰 ({len(history)}회)"
        elif last_status == "낙찰":
            final_result = f"낙찰 ({last_event.get('price', '')})"
        else:
            final_result = last_status
    else:
        if any(kw in status for kw in ["낙찰", "취소", "취하", "정지", "종결"]):
            is_ended = True
            final_result = status

    parsed_data["status"] = status
    parsed_data["is_ended"] = is_ended
    parsed_data["final_date"] = final_date
    parsed_data["final_result"] = final_result or status

    page_text = soup2.get_text(" ", strip=True)
    doc_texts = []
    documents = []
    downloaded_pdfs = []
    mulgun_pdf_text = ""
    mun_doc_text = ""

    safe_case = case_number.replace(" ", "_").replace("/", "_")
    pdf_save_dirs = [
        os.path.join(project_root, "downloads", safe_case),
        os.path.join(project_root, "downloads", case_number),
    ]

    if idx:
        doc_types = {
            "물건명세서": "mul",
            "현황조사서": "status",
            "문건접수내역": "mun",
            "송달처리내역": "song",
            "감정평가서": "judgement",
            "등기부": "aceeaea1",
            "건축물대장": "aceeair",
        }
        for name, t in doc_types.items():
            doc_url = f"{MYAUCTION_BASE}/auction/auction_detail_view.php?type={t}&idx={idx}"
            documents.append({"name": f"{name}.pdf", "url": doc_url})
            if sess is not None:
                try:
                    dr = sess.get(doc_url, timeout=(4, 8))
                    if dr.status_code == 200:
                        d_html = dr.text
                        if "열람이 중지" in d_html or "열람제한" in d_html:
                            parsed_data["viewing_suspended"] = True
                            if name not in parsed_data["suspended_documents"]:
                                parsed_data["suspended_documents"].append(name)
                        else:
                            d_soup = BeautifulSoup(d_html, "html.parser")
                            # iframe 내 실제 PDF 파일(예: Mulgun.pdf, PDF_Judgement.pdf) 감지 및 원문 추출
                            iframe = d_soup.find("iframe")
                            iframe_src = (iframe.get("src") or "").strip() if iframe else ""
                            if iframe_src:
                                if iframe_src.startswith("//"):
                                    iframe_src = "https:" + iframe_src
                                elif iframe_src.startswith("/"):
                                    iframe_src = MYAUCTION_BASE + iframe_src
                                documents[-1]["pdf_url"] = iframe_src
                                if ".pdf" in iframe_src.lower() and t in ("mul", "judgement"):
                                    try:
                                        pdf_resp = sess.get(
                                            iframe_src,
                                            headers={"Referer": f"{MYAUCTION_BASE}/"},
                                            timeout=(5, 12),
                                        )
                                        if pdf_resp.status_code == 200 and len(pdf_resp.content) > 500:
                                            pdf_filename = "매각물건명세서.pdf" if t == "mul" else f"{name}.pdf"
                                            for pdir in pdf_save_dirs:
                                                os.makedirs(pdir, exist_ok=True)
                                                with open(os.path.join(pdir, pdf_filename), "wb") as pf:
                                                    pf.write(pdf_resp.content)
                                            if pdf_filename not in downloaded_pdfs:
                                                downloaded_pdfs.append(pdf_filename)

                                            extracted_pdf_txt = ""
                                            try:
                                                import io
                                                import pypdf
                                                reader = pypdf.PdfReader(io.BytesIO(pdf_resp.content))
                                                extracted_pdf_txt = "\n".join(
                                                    (pg.extract_text() or "") for pg in reader.pages
                                                ).strip()
                                            except Exception:
                                                try:
                                                    import io
                                                    import pdfplumber
                                                    with pdfplumber.open(io.BytesIO(pdf_resp.content)) as pl_pdf:
                                                        extracted_pdf_txt = "\n".join(
                                                            (pg.extract_text() or "") for pg in pl_pdf.pages
                                                        ).strip()
                                                except Exception as pdf_ex:
                                                    print(f"[MyAuction PDF] {pdf_filename} 텍스트 추출 경고: {pdf_ex}")

                                            if extracted_pdf_txt:
                                                doc_texts.append(f"=== [{pdf_filename} (법원 원문 PDF 추출)] ===\n{extracted_pdf_txt[:10000]}")
                                                if t == "mul":
                                                    mulgun_pdf_text = extracted_pdf_txt
                                                    page_text += " " + extracted_pdf_txt
                                    except Exception as dl_err:
                                        print(f"[MyAuction PDF] {name} PDF 다운로드 경고: {dl_err}")

                            for tag in d_soup(["script", "style"]):
                                tag.decompose()
                            clean_doc = d_soup.get_text("\n", strip=True)
                            if len(clean_doc) > 120 and not (t in ("mul", "judgement") and mulgun_pdf_text):
                                doc_texts.append(f"=== [{name}] ===\n{clean_doc[:6000]}")
                                if t in ("mul", "mun", "status"):
                                    page_text += " " + clean_doc
                                if t == "mun":
                                    mun_doc_text = clean_doc
                except Exception as e:
                    print(f"[MyAuction HTTP] {name} 텍스트 조회 경고: {e}")

        # 건물 등기부현황 요약표(pageview mode=2) 추가 수집
        if sess is not None:
            try:
                rp2 = sess.post(
                    f"{MYAUCTION_BASE}/auction/pageview.php",
                    data={"mode": "2", "str": idx, "str2": "Y"},
                    timeout=(4, 6),
                )
                if rp2.status_code == 200 and len(rp2.text) > 100:
                    s_reg = BeautifulSoup(rp2.text, "html.parser")
                    for tag in s_reg(["script", "style"]):
                        tag.decompose()
                    reg_txt = s_reg.get_text("\n", strip=True)
                    if reg_txt:
                        doc_texts.append(f"=== [건물 등기부현황 요약] ===\n{reg_txt[:4000]}")
                        page_text += " " + reg_txt
            except Exception as reg_e:
                print(f"[MyAuction HTTP] 등기부현황 요약 조회 경고: {reg_e}")

    parsed_data["documents"] = documents
    parsed_data["downloaded_pdfs"] = downloaded_pdfs
    parsed_data["mulgun_pdf_text"] = mulgun_pdf_text
    if doc_texts:
        parsed_data["scraped_doc_text"] = "\n\n".join(doc_texts)

    combined_hug_source = f"{page_text}\n{parsed_data.get('precautions', '')}\n{mulgun_pdf_text}\n{mun_doc_text}"
    page_text_clean = re.sub(r"\s+", "", combined_hug_source)
    has_hug_keyword = (
        "주택도시보증공사" in page_text_clean
        or "주식도시보증공사" in page_text_clean
        or "HUG" in combined_hug_source.upper()
    )
    has_waive_keyword = any(
        kw in page_text_clean
        for kw in [
            "대항력포기",
            "청구권포기",
            "청구권을포기",
            "보증금반환채권을포기",
            "우선매수권포기",
            "잔존임대차보증금",
            "잔존임차보증금",
            "말소동의",
            "말소에동의",
            "확약서를제출",
            "확약서가제출",
            "확약서제출",
            "인수조건변경",
            "인수할사항없음",
        ]
    )
    hug_waived = has_hug_keyword and has_waive_keyword
    hug_court_submitted = bool(
        hug_waived
        and (
            any(k in page_text_clean for k in ["확약서를제출", "확약서가제출", "확약서제출", "말소동의확약서"])
            or ("주택도시보증공사" in re.sub(r"\s+", "", mulgun_pdf_text))
        )
    )

    hug_evidence_lines = []
    if hug_waived:
        source_for_ev = mulgun_pdf_text if mulgun_pdf_text else f"{parsed_data.get('precautions', '')}\n{mun_doc_text}"
        for raw_ln in source_for_ev.splitlines():
            s_ln = re.sub(r"\s+", " ", raw_ln).strip()
            if any(k in s_ln for k in ["주택도시보증공사", "HUG", "확약서", "말소동의", "말소에 동의", "반환채권을 포기", "대항력포기", "인수조건변경"]):
                if s_ln and s_ln not in hug_evidence_lines:
                    hug_evidence_lines.append(s_ln)

    parsed_data["hug_waived"] = hug_waived
    parsed_data["hug_court_submitted"] = hug_court_submitted
    parsed_data["hug_mulgun_pdf_verified"] = bool(mulgun_pdf_text and hug_waived)
    parsed_data["hug_waiver_evidence"] = " / ".join(hug_evidence_lines[:5])

    risks = parsed_data["risks"]
    if hug_waived:
        if "대항력 임차인" in risks:
            risks.remove("대항력 임차인")
        if "HUG 대항력포기" not in risks:
            risks.append("HUG 대항력포기")

    if "법정지상권" in page_text and "법정지상권" not in risks:
        risks.append("법정지상권")
    if "유치권" in page_text and "유치권" not in risks:
        risks.append("유치권")

    has_no_tenant = ("조사된임차내역이없습니다" in page_text_clean) and len(tenants) == 0
    parsed_data["has_tenant"] = not has_no_tenant
    if has_no_tenant:
        if "대항력 임차인" in risks:
            risks.remove("대항력 임차인")
    else:
        if "대항력" in page_text and "임차인" in page_text and "대항력 임차인" not in risks and not hug_waived:
            risks.append("대항력 임차인")

    if "선순위" in page_text and "전세권" in page_text and "선순위 전세권" not in risks and "인수되는 전세권" not in risks:
        risks.append("선순위 전세권")
    if "선순위" in page_text and "가등기" in page_text and "선순위 가등기" not in risks:
        risks.append("선순위 가등기")

    parsed_data["risks"] = risks
    return parsed_data


def _download_case_images_from_soup(soup2: BeautifulSoup, case_number: str, sess: requests.Session) -> str:
    """상세 HTML 내 물건 사진(전경·위치도·구조도) 최대 3장을 다운로드 폴더에 저장합니다."""
    safe_case = case_number.replace(" ", "_").replace("/", "_")
    dirs = [
        os.path.join(project_root, "downloads", safe_case),
        os.path.join(project_root, "downloads", case_number),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    imgs = soup2.select('img[src*="photo.nuriauction.com"], .photo_list img, .photo img, #img_1, .img_wrap img, .view_img img')
    srcs = []
    for im in imgs:
        src = (im.get("src") or "").strip()
        if not src or any(skip in src.lower() for skip in ["logo", "icon", "btn_", "banner", "blank"]):
            continue
        if src.startswith("//"):
            src = "https:" + src
        elif src.startswith("/"):
            src = MYAUCTION_BASE + src
        elif not src.startswith("http"):
            src = f"{MYAUCTION_BASE}/{src.lstrip('./')}"
        if src not in srcs:
            srcs.append(src)

    if len(srcs) >= 3:
        chosen = [srcs[0], srcs[-2], srcs[-1]]
    else:
        chosen = srcs[:3]

    saved_names = ["photo.jpg", "map.jpg", "structure.jpg"]
    saved_any = False
    for i, url in enumerate(chosen):
        if i >= 3:
            break
        try:
            r = sess.get(url, timeout=(4, 8))
            if r.status_code == 200 and len(r.content) > 800:
                for d in dirs:
                    with open(os.path.join(d, saved_names[i]), "wb") as f:
                        f.write(r.content)
                saved_any = True
        except Exception as e:
            print(f"[MyAuction HTTP] 이미지 다운로드 실패 ({url}): {e}")

    return f"/api/download_photo/{case_number}" if saved_any else "/test_images/thumb_0.png"


def _enrich_item_detail_summary(sess: requests.Session, item_data: Dict[str, Any]) -> Dict[str, Any]:
    full_url = item_data.pop("_detail_url", "")
    if not full_url:
        return item_data
    try:
        d_resp = sess.get(full_url, timeout=(4, 8))
        if d_resp.status_code == 200:
            d_soup = BeautifulSoup(d_resp.text, "html.parser")
            for th in d_soup.find_all("th"):
                t_lbl = th.get_text(" ", strip=True)
                td = th.find_next_sibling("td")
                if not td:
                    continue
                val = td.get_text(" ", strip=True)
                if "감정가" in t_lbl and not item_data["appraised_value"]:
                    item_data["appraised_value"] = re.sub(r"[^0-9]", "", val.split("%")[-1])
                if "최저가" in t_lbl and not item_data["minimum_value"]:
                    item_data["minimum_value"] = re.sub(r"[^0-9]", "", val.split("%")[-1])
                if any(k in t_lbl for k in ["보존", "승인", "준공", "연식", "연도", "검사", "신축"]) and not item_data["approval_date"]:
                    item_data["approval_date"] = val
                if "물건종류" in t_lbl and not item_data["property_type"]:
                    item_data["property_type"] = val
                if "건물면적" in t_lbl and not item_data["building_area"]:
                    item_data["building_area"] = val
                if "토지면적" in t_lbl and not item_data["land_area"]:
                    item_data["land_area"] = val
                if "매각기일" in t_lbl and not item_data.get("sale_date"):
                    item_data["sale_date"] = val.split(" ")[0] if val else ""
            if not item_data["approval_date"]:
                fm = re.search(
                    r"(?:사용승인|보존등기|사용검사|준공|신축)[^\d]*(\d{4}[\.\-년]\s*\d{1,2}[\.\-월])",
                    d_resp.text,
                )
                if fm:
                    item_data["approval_date"] = fm.group(1)
    except Exception as pe:
        print(f"[MyAuction HTTP] 상세 요약 파싱 경고: {pe}")
    return item_data


def _search_myauction_http_sync(case_number: str) -> Dict[str, Any]:
    comp = parse_case_components(case_number)
    clean_case = comp["clean"]
    is_public_sale = comp["is_public_sale"]

    if "2026-0400" in clean_case:
        return {
            "success": True,
            "items": [{
                "case_no_full": case_number.strip(),
                "item_no": "",
                "court": "온비드 공매",
                "myauction_idx": "",
                "exact_item_match": True,
                "address": "서울특별시 강남구 테헤란로 123 (역삼동, 역삼빌딩) 101호",
                "status": "진행중",
                "raw_text": "[공매] 2026-0400-023211 서울특별시 강남구 역삼동 진행중",
                "appraised_value": "1500000000",
                "minimum_value": "1200000000",
                "approval_date": "2015.05.10",
                "property_type": "아파트",
            }],
        }

    year, num, req_item_no, court_hint = comp["year"], comp["num"], comp["item_no"], comp["court_hint"]
    if not is_public_sale and (not year or not num):
        return {"success": False, "message": "올바른 사건번호 형식이 아닙니다 (예: 2025타경51673(1) 또는 2024타경5020)"}

    sess = _create_logged_in_session()
    items: List[Dict[str, Any]] = []
    seen_idx = set()

    try:
        if is_public_sale:
            resp = sess.get(
                f"{MYAUCTION_BASE}/auction/public.php",
                params={"cltr_mnmt_no": clean_case},
                timeout=(5, 12),
            )
        else:
            resp = sess.get(
                f"{MYAUCTION_BASE}/auction/search_list.php",
                params={"aresult": "all", "sno": year, "tno": num},
                timeout=(5, 12),
            )

        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            rows = soup.select("table.tbl_auction_list tr, table.list-table tr, table tr")

            for tr in rows:
                row_text = tr.get_text("\n", strip=True)
                if not row_text or "용도/사건" in row_text or ("소재지" in row_text and "감정가" in row_text):
                    continue
                row_clean = row_text.replace(" ", "")

                row_item_no = ""
                if is_public_sale:
                    if clean_case not in row_clean:
                        continue
                    case_no_full = clean_case
                else:
                    m_row = re.search(rf"{year}-0*{int(num)}(?:\((\d+)\))?(?!\d)", row_clean)
                    if not m_row:
                        continue
                    row_item_no = m_row.group(1) or ""
                    case_no_full = f"{year} 타경 {num}({row_item_no})" if row_item_no else f"{year} 타경 {num}"

                link = tr.select_one("a[href*='/view/'], a[href*='idx=']")
                href = link.get("href") if link else ""
                idx_m = re.search(r"/view/(\d+)", href or "") or re.search(r"idx=(\d+)", href or "")
                row_idx = idx_m.group(1) if idx_m else ""
                if row_idx and row_idx in seen_idx:
                    continue

                lines = [ln.strip() for ln in row_text.splitlines() if ln.strip()]
                address = ""
                status = ""
                court_name = ""
                prop_type_hint = ""
                sale_date_hint = ""

                for i_ln, ln in enumerate(lines):
                    if i_ln == 0 and len(ln) <= 12 and not any(ch.isdigit() for ch in ln):
                        prop_type_hint = ln
                    if any(k in ln for k in ["지방법원", "지원", "법원"]) and len(ln) <= 18 and not court_name:
                        court_name = ln
                    if ("시" in ln or "도" in ln or "동" in ln or "군" in ln or "구" in ln) and len(ln) > 9 and not address:
                        if not any(k in ln for k in ["지방법원", "지원"]):
                            address = ln
                    if any(k in ln for k in ["유찰", "진행", "신건", "낙찰", "매각", "미납", "변경", "취하", "정지", "취소"]):
                        if len(ln) <= 20:
                            status = ln
                    m_dt = re.match(r"^(\d{4}-\d{2}-\d{2})$", ln)
                    if m_dt and not sale_date_hint:
                        sale_date_hint = m_dt.group(1)

                if not address:
                    continue
                if row_idx:
                    seen_idx.add(row_idx)

                exact_item = bool(req_item_no and row_item_no == req_item_no)
                court_matched = bool(court_hint and court_hint in court_name)
                is_active_status = not any(k in (status or "") for k in ["매각", "낙찰", "취하", "취소", "종결"])

                sort_score = 0
                if req_item_no:
                    sort_score += 2000 if exact_item else -300
                if court_hint:
                    sort_score += 500 if court_matched else -100
                if is_active_status:
                    sort_score += 100

                full_url = (href if href.startswith("http") else f"{MYAUCTION_BASE}{href}") if href else ""
                items.append({
                    "case_no_full": case_no_full,
                    "item_no": row_item_no,
                    "court": court_name,
                    "myauction_idx": row_idx,
                    "exact_item_match": exact_item,
                    "address": address,
                    "status": status or "진행중",
                    "sale_date": sale_date_hint,
                    "raw_text": row_text.replace("\n", " "),
                    "appraised_value": "",
                    "minimum_value": "",
                    "approval_date": "",
                    "property_type": prop_type_hint,
                    "building_area": "",
                    "land_area": "",
                    "_detail_url": full_url,
                    "_sort_score": sort_score,
                })

            if items:
                from concurrent.futures import ThreadPoolExecutor
                with ThreadPoolExecutor(max_workers=min(6, len(items))) as pool:
                    items = list(pool.map(lambda it: _enrich_item_detail_summary(sess, it), items))

                items.sort(
                    key=lambda x: (
                        -x.get("_sort_score", 0),
                        int(x["item_no"]) if str(x.get("item_no", "")).isdigit() else 999,
                    )
                )
                for it in items:
                    it.pop("_sort_score", None)
    except Exception as e:
        print(f"[MyAuction HTTP] 목록 조회 예외 (DB 폴백 진행): {e}")

    if items:
        return {
            "success": True,
            "items": items,
            "has_sub_number": bool(req_item_no or comp["has_parenthesis"]),
            "requested_item_no": req_item_no,
        }

    # 폴백: 로컬 map_data.db (auctions 테이블) 조회
    db_items = _lookup_local_auctions_db(case_number)
    if db_items:
        print(f"[{case_number}] 로컬 map_data.db 폴백으로 {len(db_items)}건 반환")
        return {
            "success": True,
            "items": db_items,
            "has_sub_number": bool(req_item_no or comp["has_parenthesis"]),
            "requested_item_no": req_item_no,
        }

    return {"success": True, "items": [], "has_sub_number": bool(req_item_no)}


def _scrape_myauction_http_sync(
    case_number: str,
    address_hint: str = "",
    myauction_idx: str = "",
) -> Dict[str, Any]:
    comp = parse_case_components(case_number)
    clean_case = comp["clean"]
    is_public_sale = comp["is_public_sale"]
    year, num, req_item_no, court_hint = comp["year"], comp["num"], comp["item_no"], comp["court_hint"]

    if "2026-0400" in clean_case:
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
                "precautions": "[주의사항] 본건은 공매물건으로서 압류재산(세무서 등)에 의한 매각임.",
                "has_tenant": True,
                "documents": [],
                "history": [],
                "pdf_text": "공매재산명세서\n압류기관: 강남세무서\n체납액: 50,000,000원\n법정기일: 2018.03.01\n임차인: 김철수, 전입일: 2018.05.01\n대항력 있음. 보증금미상.",
            },
            "message": "MOCK 공매 데이터 크롤링 완료",
        }

    if not is_public_sale and (not year or not num):
        return {"success": False, "error": "올바른 사건번호 형식이 아닙니다 (예: 2025타경51673(1) 또는 2024타경1234)"}

    sess = _create_logged_in_session()
    chosen_detail_url = ""
    row_status = "진행중"

    try:
        # 1순위: 물건 선택 화면에서 전달된 고유 myauction_idx 직접 조회 (오매칭 0%)
        clean_idx = str(myauction_idx or "").strip()
        if clean_idx.isdigit():
            chosen_detail_url = f"{MYAUCTION_BASE}/view/{clean_idx}"
            print(f"[{case_number}] 선택된 고유 물건 ID(idx={clean_idx}) 직접 조회 실행")
        else:
            # 2순위: 사건번호 + 괄호 물건번호((1) 등) + 지번 포함 전체 주소 토큰 정밀 스코어링
            if is_public_sale:
                s_resp = sess.get(
                    f"{MYAUCTION_BASE}/auction/public.php",
                    params={"cltr_mnmt_no": clean_case},
                    timeout=(5, 12),
                )
            else:
                s_resp = sess.get(
                    f"{MYAUCTION_BASE}/auction/search_list.php",
                    params={"aresult": "all", "sno": year, "tno": num},
                    timeout=(5, 12),
                )

            if s_resp.status_code == 200:
                soup = BeautifulSoup(s_resp.text, "html.parser")
                rows = soup.select("table.tbl_auction_list tr, table.list-table tr, table tr")
                hint_tokens = [t for t in re.split(r"[\s,]+", (address_hint or "").strip()) if len(t) >= 2]

                candidates = []
                for tr in rows:
                    rtxt = tr.get_text("\n", strip=True)
                    rclean = rtxt.replace(" ", "")
                    if is_public_sale:
                        if clean_case not in rclean:
                            continue
                        row_item_no = ""
                    else:
                        m_row = re.search(rf"{year}-0*{int(num)}(?:\((\d+)\))?(?!\d)", rclean)
                        if not m_row:
                            continue
                        row_item_no = m_row.group(1) or ""

                    a_tag = tr.select_one("a[href*='/view/'], a[href*='idx=']")
                    if not a_tag or not a_tag.get("href"):
                        continue

                    score = 0
                    if req_item_no:
                        score += 2000 if row_item_no == req_item_no else -2000
                    if court_hint and court_hint in rclean:
                        score += 300
                    for kt in hint_tokens:
                        if kt in rtxt or kt in rclean:
                            # 지번(숫자-숫자 또는 단독 지번) 일치에 높은 가중치 부여
                            score += 150 if any(ch.isdigit() for ch in kt) else 40
                    candidates.append((score, a_tag.get("href"), rtxt))

                if candidates:
                    candidates.sort(key=lambda x: x[0], reverse=True)
                    best_score, chosen_href, matched_row_text = candidates[0]
                    for line in [l.strip() for l in matched_row_text.splitlines() if l.strip()]:
                        if any(kw in line for kw in ["유찰", "진행", "신건", "낙찰", "매각", "미납", "변경", "취소", "취하", "정지"]):
                            row_status = line
                            break
                    chosen_detail_url = chosen_href if chosen_href.startswith("http") else f"{MYAUCTION_BASE}{chosen_href}"
                    print(f"[{case_number}] 정밀 매칭 선택 완료 (score={best_score}, url={chosen_detail_url})")

        if chosen_detail_url:
            d_resp = sess.get(chosen_detail_url, timeout=(5, 12))
            if d_resp.status_code == 200:
                idx_m = re.search(r"/view/(\d+)", chosen_detail_url) or re.search(r"idx=(\d+)", chosen_detail_url)
                idx = idx_m.group(1) if idx_m else None
                soup2 = BeautifulSoup(d_resp.text, "html.parser")
                parsed_data = _parse_detail_html(soup2, d_resp.text, case_number, row_status, idx, sess=sess)
                parsed_data["photo_url"] = _download_case_images_from_soup(soup2, case_number, sess)
                parsed_data.setdefault("downloaded_pdfs", [])
                parsed_data["myauction_idx"] = idx or ""

                # 로컬 DB 보완 (동일 물건번호 기준 면적/매각기일/좌표 등 빈 값 보강)
                db_rows = _lookup_local_auctions_db(case_number, parsed_data.get("address") or address_hint)
                if db_rows:
                    dbr = db_rows[0]
                    if not parsed_data.get("address"):
                        parsed_data["address"] = dbr.get("address", "")
                    if not parsed_data.get("appraised_value"):
                        parsed_data["appraised_value"] = dbr.get("appraised_value", "")
                    if not parsed_data.get("minimum_value"):
                        parsed_data["minimum_value"] = dbr.get("minimum_value", "")
                    if not parsed_data.get("building_area"):
                        parsed_data["building_area"] = dbr.get("building_area", "")
                    if not parsed_data.get("land_area"):
                        parsed_data["land_area"] = dbr.get("land_area", "")
                    if not parsed_data.get("auction_date"):
                        parsed_data["auction_date"] = dbr.get("sale_date", "")
                    if dbr.get("lat") and dbr.get("lng"):
                        parsed_data["lat"] = dbr.get("lat")
                        parsed_data["lng"] = dbr.get("lng")

                print(f"[{case_number}] 고속 HTTP 상세 파싱 완료: {parsed_data.get('address')} (감정가={parsed_data.get('appraised_value')})")
                return {"success": True, "data": parsed_data, "message": "크롤링 완료 (고속 HTTP)"}
    except Exception as e:
        print(f"[{case_number}] 마이옥션 HTTP 상세 크롤링 예외: {e}")

    # 폴백: 로컬 map_data.db (auctions 테이블) 기반 구성
    db_rows = _lookup_local_auctions_db(case_number, address_hint)
    if db_rows:
        dbr = db_rows[0]
        notes = str(dbr.get("special_notes") or "")
        risks = []
        for kw, lbl in [
            ("위반건축물", "위반건축물"),
            ("유치권", "유치권"),
            ("법정지상권", "법정지상권"),
            ("지분", "지분매각"),
            ("대항력", "대항력 임차인"),
            ("선순위", "선순위 권리"),
            ("임차권등기", "임차권등기"),
        ]:
            if kw in notes and lbl not in risks:
                risks.append(lbl)
        hug_waived_db = False
        if ("HUG" in notes.upper() or "주택도시보증공사" in notes) and any(k in notes for k in ["포기", "인수조건변경", "확약", "말소동의"]):
            hug_waived_db = True
            if "대항력 임차인" in risks:
                risks.remove("대항력 임차인")
            if "HUG 대항력포기" not in risks:
                risks.append("HUG 대항력포기")

        parsed_data = {
            "case_number": dbr.get("case_no_full") or case_number,
            "status": "진행중",
            "is_ended": False,
            "final_date": dbr.get("sale_date", ""),
            "final_result": "진행중",
            "property_type": dbr.get("property_type", "부동산"),
            "appraised_value": dbr.get("appraised_value", ""),
            "minimum_value": dbr.get("minimum_value", ""),
            "address": dbr.get("address", address_hint),
            "approval_date": "",
            "auction_date": dbr.get("sale_date", ""),
            "land_area": dbr.get("land_area", ""),
            "building_area": dbr.get("building_area", ""),
            "lat": dbr.get("lat"),
            "lng": dbr.get("lng"),
            "risks": risks,
            "precautions": f"[DB 특이사항] {notes}" if notes and notes not in ("0 # A 미해당",) else "",
            "tenants": [],
            "tenant_comments": [],
            "viewing_suspended": False,
            "suspended_documents": [],
            "documents": [],
            "history": [],
            "has_tenant": ("임차" in notes or "대항력" in notes),
            "hug_waived": hug_waived_db,
            "hug_court_submitted": False,
            "hug_mulgun_pdf_verified": False,
            "hug_waiver_evidence": f"[DB 특이사항 감지] {notes} (원본 매각물건명세서.pdf 별도 대조 권장)" if hug_waived_db else "",
            "photo_url": "/test_images/thumb_0.png",
            "downloaded_pdfs": [],
        }
        print(f"[{case_number}] 로컬 map_data.db 폴백으로 상세 데이터 구성 완료: {parsed_data.get('address')}")
        return {"success": True, "data": parsed_data, "message": "크롤링 완료 (로컬 경매 DB 폴백)"}

    return {"success": False, "error": f"[{case_number}] 검색 결과를 찾을 수 없습니다. 사건번호를 확인해주세요."}


async def search_myauction_list(case_number: str):
    """사건번호로 마이옥션 및 로컬 경매 DB를 고속 검색하여 물건 목록을 반환합니다."""
    print(f"[{case_number}] 사건번호 주소 목록 검색 시작...")
    return await asyncio.to_thread(_search_myauction_http_sync, case_number)


async def scrape_myauction_case(case_number: str, address_hint: str = "", myauction_idx: str = ""):
    """사건번호 및 고유 물건 ID(myauction_idx)의 상세 권리·임차·기일·문서 데이터를 고속 수집합니다."""
    print(f"[{case_number}] 마이옥션 크롤링 시작 (idx={myauction_idx or 'auto'})...")
    return await asyncio.to_thread(_scrape_myauction_http_sync, case_number, address_hint, myauction_idx)


if __name__ == "__main__":
    print(asyncio.run(search_myauction_list("2025 타경 51673(1)")))
