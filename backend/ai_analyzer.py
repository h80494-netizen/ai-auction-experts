import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

def generate_deep_research(data: dict) -> str:
    """
    제미나이 2.5 Flash 기반 20년 경매 전문가 9단계 심층 분석 파이프라인
    """
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path=env_path)
    
    api_keys_env = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_keys_env:
        return "⚠️ Gemini API 키가 설정되지 않아 심층 분석을 건너뛰었습니다."
    
    api_keys = [k.strip() for k in api_keys_env.split(',') if len(k.strip()) > 20]
    if not api_keys:
        return f"⚠️ 유효하지 않은 Gemini API 키 형식입니다: {api_keys_env[:10]}..."

    try:
        
        # Parse data safely
        try:
            appraised_value = int(data.get('appraised_value', 0))
            minimum_value = int(data.get('minimum_value', 0))
        except:
            appraised_value = 0
            minimum_value = 0
            
        case_number = data.get('case_number', '알 수 없음')
        address = data.get('address', '알 수 없음')
        approval_date = data.get('approval_date', '알 수 없음')
        auction_date = data.get('auction_date', '알 수 없음')
        land_area = data.get('land_area', '알 수 없음')
        building_area = data.get('building_area', '알 수 없음')
        risks = ', '.join(data.get('risks', [])) if data.get('risks') else '특이사항 없음'
        precautions = data.get('precautions', '없음')
        
        status = data.get('status', '진행중')
        is_ended = data.get('is_ended', False)
        final_date = data.get('final_date', '')
        final_result = data.get('final_result', '')
        
        history_str = ""
        if data.get("history"):
            history_str = "\n".join([f"- {h.get('date')}: 최저입찰가 {h.get('price')} ({h.get('status')})" for h in data.get("history")])
        else:
            history_str = "없음"
            
        property_type = data.get('property_type', '주택')
        raw_hc = str(data.get('house_count', '0'))
        if raw_hc in ['0', '무주택', '0주택']:
            house_count = '무주택 (0주택)'
        elif raw_hc in ['1', '1주택']:
            house_count = '1주택'
        elif raw_hc in ['2', '2주택']:
            house_count = '2주택'
        else:
            house_count = '3주택 이상' if raw_hc in ['3', '3주택 이상'] else f'{raw_hc}주택'
        investor_type = data.get('investor_type', '개인')
        investment_duration = data.get('investment_duration', '단기(6개월)')
        target_return = data.get('target_return_rate') or data.get('target_return') or '20'
        is_regulated = data.get('is_regulated_area', False)
        has_tenant = data.get('has_tenant', True)
        
        regulated_str = "조정대상지역" if str(is_regulated).lower() == 'true' else "비조정대상지역"
        
        ended_warning = ""
        if is_ended:
            ended_warning = f"\n\n**[중요: 과거/종결된 사건]**\n본 사건은 최종 날짜 {final_date}에 '{final_result}' 상태로 종결된 과거 사건입니다. 따라서 보고서 분석 및 추천입찰가 역산 시 이미 종결된 물건임을 감안하여 보고서를 서술해 주십시오.\n"

        tenant_warning = ""
        if not has_tenant:
            tenant_warning = "\n\n**[초강력 경고: 임차인 없음]**\n본 경매 물건은 법원 현황조사 결과 **임차인이 전혀 없는 물건**으로 확인되었습니다. 따라서 권리분석, 대항력, 인수 보증금, 가장임차인, 명도(세입자 퇴거) 등 **임차인과 관련된 그 어떠한 내용이나 단어도 보고서 전체에서 일절 언급하지 마십시오.** (임차인 관련 항목은 아예 지워버리세요.)\n"
        
        # 법원 서류 열람 관련 안내 문구 생략 (사용자 요청에 따라 완전 생략)
        suspended_warning = ""

        # 로컬 PDF 텍스트 추출 우선 연동 (Dual-Engine)
        pdf_texts = []
        if 'downloaded_pdfs' in data and data['downloaded_pdfs']:
            try:
                from parser.pdf_extractor import extract_text_from_pdf
                for pdf_path in data['downloaded_pdfs']:
                    name = os.path.basename(pdf_path)
                    print(f"로컬 PDF 텍스트 추출 중: {pdf_path}")
                    txt = extract_text_from_pdf(pdf_path)
                    if txt and not txt.startswith("Error"):
                        pdf_texts.append(f"=== {name} 텍스트 시작 ===\n{txt}\n=== {name} 텍스트 끝 ===")
                    else:
                        print(f"로컬 텍스트 추출 실패/건너뜀 ({name}): {txt}")
            except Exception as pe:
                print(f"로컬 PDF 파서 로딩 에러: {pe}")
                
        if pdf_texts:
            pdf_context = "\n\n".join(pdf_texts)
        else:
            pdf_context = data.get('pdf_text', '첨부된 PDF 텍스트가 없습니다. 마이옥션에서 수집된 기본 정보만으로 분석합니다.')

        # 구조화된 임차인 정보 포맷팅
        tenants_list = data.get("tenants", [])
        tenant_comments_list = data.get("tenant_comments", [])
        
        tenants_str = ""
        if tenants_list:
            tenants_str += "### [정밀 수집된 임차인 현황 (마이옥션 및 법원 서류 기반)]\n"
            for t in tenants_list:
                tenants_str += f"- 임차인명: {t.get('name')}\n"
                tenants_str += f"  * 점유부분/용도: {t.get('usage')}\n"
                tenants_str += f"  * 전입일자: {t.get('transfer_date') or '미상'}\n"
                tenants_str += f"  * 확정일자: {t.get('confirmation_date') or '미상'}\n"
                tenants_str += f"  * 배당요구일: {t.get('claim_date') or '미상'}\n"
                tenants_str += f"  * 보증금/월세 원문: {t.get('deposit_rent') or '미상'}\n"
                tenants_str += f"  * 추출된 보증금: {t.get('deposit', 0):,} 원\n"
                tenants_str += f"  * 추출된 월세: {t.get('rent', 0):,} 원\n"
                tenants_str += f"  * 대항력 여부: {t.get('has_opposing_power') or 'X'}\n"
                tenants_str += f"  * 비고: {t.get('remarks') or '없음'}\n"
        else:
            tenants_str += "### [정밀 수집된 임차인 현황]\n- 수집된 임차인 현황이 없거나 조사된 임차인 내역이 없습니다.\n"
            
        if tenant_comments_list:
            tenants_str += "\n### [매각물건명세서 및 현황조사서 특이사항/주석]\n"
            for c in tenant_comments_list:
                tenants_str += f"- {c}\n"

        # 공매(Gongmae) 여부 판별
        is_gongmae = "-" in str(case_number) and "타경" not in str(case_number)
        gongme_type = data.get("gongme_type", "압류재산")
        gongmae_instructions = ""
        if is_gongmae:
            gongmae_instructions = f"""
**[공매(온비드) 특화 권리분석 지침]**
본 건은 법원 경매가 아닌 한국자산관리공사(KAMCO) 등 주관의 **'공매({gongme_type})'** 물건입니다. 공매 재산의 종류('{gongme_type}')에 따라 다음 사항을 반드시 적용하십시오.
1) **공매 재산 종류에 따른 분석 기준 차이**:
   - **압류재산**: 법원 경매와 동일하게 '말소기준권리'를 적용하여 권리의 인수/소멸 여부를 판단합니다. 임차인의 '배분요구'와 당해세/조세채권 법정기일을 분석하여 낙찰자 인수금액을 산정하십시오.
   - **신탁재산(수의계약 포함) 및 기타일반재산**: 신탁공매 등은 **'말소기준권리' 제도가 원칙적으로 적용되지 않으며, 매수인이 기존 제한물권(근저당, 압류, 임차권 등)을 그대로 인수**하는 조건일 가능성이 매우 높습니다(단, 공매공고에 '매도자 책임 말소' 조건이 명시된 경우는 예외). 따라서 신탁공매나 수의계약 건인 경우, "말소기준권리로 소멸된다"는 식의 법원경매식 권리분석을 절대 금지하며, 공고문 상의 인수조건을 철저히 확인해야 한다는 점을 가장 강력하게 경고하십시오.
2) **배분요구(교부청구)**: 압류재산의 경우 배분요구 종기가 매우 중요합니다.
3) **인수 금액 리스크 (조세채권 우선 원칙)**: 압류재산의 경우, 법정기일이 빠른 국세/지방세가 먼저 배분되어 임차인이 배분받지 못하는 금액이 발생 시 매수인에게 전액 인수됩니다.
4) **명도 책임**: 공매는 인도명령 제도가 없으므로 명도소송 및 명도 책임이 전적으로 매수인(낙찰자)에게 있음을 명시하십시오.
"""

        import datetime
        current_year = datetime.datetime.now().year

        prompt_file_path = os.path.join(os.path.dirname(__file__), "prompts", "deep_research_prompt.md")
        try:
            with open(prompt_file_path, "r", encoding="utf-8") as pf:
                prompt = pf.read()
        except FileNotFoundError:
            raise Exception("프롬프트 파일을 찾을 수 없습니다: " + prompt_file_path)

        prompt = prompt.replace("{gongmae_instructions}", gongmae_instructions)
        prompt = prompt.replace("{current_year}", str(current_year))
        prompt = prompt.replace("{case_number}", str(case_number))
        prompt = prompt.replace("{address}", str(address))
        prompt = prompt.replace("{property_type}", str(property_type))
        prompt = prompt.replace("{appraised_value}", str(appraised_value))
        prompt = prompt.replace("{minimum_value}", str(minimum_value))
        prompt = prompt.replace("{auction_date}", str(auction_date))
        prompt = prompt.replace("{approval_date}", str(approval_date))
        prompt = prompt.replace("{land_area}", str(land_area))
        prompt = prompt.replace("{building_area}", str(building_area))
        prompt = prompt.replace("{risks}", str(risks))
        prompt = prompt.replace("{precautions}", str(precautions))
        prompt = prompt.replace("{tenant_warning}", str(tenant_warning))
        prompt = prompt.replace("{suspended_warning}", str(suspended_warning))
        prompt = prompt.replace("{ended_warning}", str(ended_warning))
        prompt = prompt.replace("{regulated_str}", str(regulated_str))
        prompt = prompt.replace("{house_count}", str(house_count))
        prompt = prompt.replace("{investor_type}", str(investor_type))
        prompt = prompt.replace("{investment_duration}", str(investment_duration))
        prompt = prompt.replace("{target_return}", str(target_return))
        prompt = prompt.replace("{status}", str(status))
        prompt = prompt.replace("{is_ended}", str(is_ended))
        prompt = prompt.replace("{final_date}", str(final_date))
        prompt = prompt.replace("{final_result}", str(final_result))
        prompt = prompt.replace("{history_str}", str(history_str))
        prompt = prompt.replace("{tenants_str}", str(tenants_str))
        prompt = prompt.replace("{pdf_context}", str(pdf_context))
        
        prompt += "\n\n**[중요 지시사항]: 응답은 반드시 '# 1. 요약'으로 시작해야 하며, 1번부터 10번까지의 목차를 빠짐없이 순서대로 작성하세요. 절대 중간 목차부터 시작하지 마세요.**\n"
        last_err_msg = ""
        for current_api_key in api_keys:
            try:
                genai.configure(api_key=current_api_key)
                model = genai.GenerativeModel('gemini-3.6-flash')
                contents = [prompt]
                uploaded_files = []
                
                # PDF 파일 업로드 및 분석 컨텍스트 추가
                if 'downloaded_pdfs' in data and data['downloaded_pdfs']:
                    import time
                    for pdf_path in data['downloaded_pdfs']:
                        try:
                            print(f"Gemini에 {pdf_path} 업로드 중...")
                            uploaded_file = genai.upload_file(path=pdf_path, mime_type="application/pdf")
                            
                            # 문서 처리 대기
                            timeout_counter = 0
                            while uploaded_file.state.name == 'PROCESSING':
                                if timeout_counter >= 30:
                                    print(f"PDF 처리 시간 초과 ({pdf_path})")
                                    break
                                print(f"{pdf_path} 처리 대기 중...")
                                time.sleep(2)
                                uploaded_file = genai.get_file(uploaded_file.name)
                                timeout_counter += 1
                                
                            if uploaded_file.state.name == 'FAILED':
                                print(f"PDF 처리 실패 상태 반환됨 ({pdf_path})")
                                continue

                            uploaded_files.append(uploaded_file)
                            contents.append(uploaded_file)
                            print(f"업로드 완료: {uploaded_file.name}")
                        except Exception as e:
                            print(f"PDF 업로드 실패 ({pdf_path}): {e}")

                safety_settings = [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                ]
                response = model.generate_content(contents, safety_settings=safety_settings)
                
                if not response.text or not response.text.strip():
                    raise Exception("AI 모델이 빈 응답을 반환했습니다. (할당량, 필터링 또는 모델 오류)")
                    
                # 분석 후 업로드된 파일 정리 (저장공간 관리)
                for uf in uploaded_files:
                    try:
                        genai.delete_file(uf.name)
                        print(f"정리 완료: {uf.name}")
                    except Exception as e:
                        print(f"파일 정리 실패 ({uf.name}): {e}")
                        
                return response.text
            except Exception as e:
                # Cleanup files on failure too
                for uf in uploaded_files:
                    try:
                        genai.delete_file(uf.name)
                    except: pass
                    
                err_msg = str(e)
                if "429" in err_msg:
                    last_err_msg = "구글 Gemini API 무료 할당량(요청 수 제한)을 초과했습니다. 잠시 후 다시 시도해주세요."
                    print(f"[{current_api_key[:10]}...] 429 할당량 초과, 다음 키 시도.")
                    continue
                elif "403" in err_msg or "빈 응답" in err_msg or "Empty" in err_msg:
                    last_err_msg = "Google Gemini API 키가 차단되었거나 빈 응답을 반환했습니다. 다른 키를 시도합니다."
                    print(f"[{current_api_key[:10]}...] 403 차단 또는 빈 응답, 다음 키 시도.")
                    continue
                
                # 그 외의 에러는 바로 중단 (예: prompt length exceed 등)
                raise Exception(f"API 호출 오류: {err_msg}")
                
        raise Exception(last_err_msg or "모든 API 키에 대해 호출이 실패했습니다. (할당량 초과 또는 권한 문제)")
                    
    except Exception as e:
        return f"⚠️ 심층 분석 중 오류 발생: {str(e)}"


def analyze_overlap_cases(items: list) -> str:
    """
    형광펜 중첩 베스트 3 물건에 대한 제미나이 2.5 Flash 기반 약식 권리분석 및 리스크/수익률 리포트 생성
    """
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path=env_path)
    
    api_keys_env = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_keys_env:
        return "⚠️ Gemini API 키가 설정되지 않아 중첩 분석을 수행할 수 없습니다."
    
    api_keys = [k.strip() for k in api_keys_env.split(',') if len(k.strip()) > 20]
    if not api_keys:
        return "⚠️ 유효하지 않은 Gemini API 키 형식입니다."
        
    try:
        
        import sys
        import os
        # Ensure crawler module is accessible
        crawler_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'crawler'))
        if crawler_path not in sys.path:
            sys.path.append(crawler_path)
            
        from crawler.onbid_scraper import scrape_onbid_case
        from crawler.search_scraper import search_expert_opinions
        from crawler.myauction_scraper import scrape_myauction_case

        # Format the items as text context
        items_context = ""
        for idx, item in enumerate(items):
            case_no = item.get('case_no', '')
            # Determine source
            is_gongmae = "-" in str(case_no) and "타경" not in str(case_no)
            source = "온비드 (공매)" if is_gongmae else "마이옥션 (경매)"
            
            expert_opinions = ""
            external_data_str = ""
            if case_no and case_no != '알 수 없음':
                # 1. Fetch from web search
                expert_opinions = search_expert_opinions(case_no)
                
                # 2. Fetch from auction/public sale scraper
                if is_gongmae:
                    onbid_data = scrape_onbid_case(case_no)
                    external_data_str = f"  * 조세채권 등: {onbid_data.get('tax_claims', '')}\n  * 당해세: {onbid_data.get('priority_tax', '')}\n  * 비고: {onbid_data.get('special_notes', '')}"
                else:
                    # 마이옥션 데이터 스크래핑 시도 (약식)
                    myauc_data = scrape_myauction_case(case_no)
                    if myauc_data and "error" not in myauc_data:
                        external_data_str = f"  * 임차인 여부: {'있음' if myauc_data.get('has_tenant') else '없음'}\n  * 법원 특이사항: {myauc_data.get('precautions', '없음')}"
            
            # Format rates and prices cleanly
            min_bid_rate = item.get('min_bid_rate', 100)
            if min_bid_rate is None:
                min_bid_rate = 100
                
            # Extra fields from frontend if present
            score_str = ""
            if 'score' in item:
                score_str = f"\n- AI 추천 지수: {item['score']}점 (100점 만점)"
            
            overlap_str = ""
            if 'overlap_count' in item:
                layers_str = ", ".join(item['matched_layers']) if item.get('matched_layers') else '없음'
                overlap_str = f"\n- 중첩된 개발계획/입지 레이어: {item['overlap_count']}개 중첩 ({layers_str})"
            
            # Get database fields
            special_notes_val = item.get('special_notes') or '없음'
            area_size = item.get('area_size', 0)
            land_size = item.get('land_size', 0)
            subway_dist = item.get('subway_dist')
            subway_dist_str = f"{subway_dist:.1f}m" if subway_dist is not None else "정보없음"
            official_land_price = item.get('official_land_price', 0)
            min_price_per_pyeong = item.get('min_price_per_pyeong', 0)
            
            items_context += f"""
### 물건 {idx+1}. {case_no} ({source})
- 소재지: {item.get('address', '알 수 없음')}
- 부동산 종류: {item.get('property_type', '알 수 없음')}
- 감정가: {item.get('appraised_value', 0):,} 원
- 최저가: {item.get('minimum_value', 0):,} 원 (감정가 대비 {min_bid_rate}%){score_str}{overlap_str}
- 특별권리분석 특이사항 (DB): {special_notes_val}
- 면적 정보: 건물 {area_size}㎡ / 대지 {land_size}㎡
- 인근 지하철역 거리: {subway_dist_str}
- 공시지가: {official_land_price:,} 원/㎡
- 평당 최저가: {min_price_per_pyeong:,} 원/평
- 스크래핑된 공매/경매 상세 특이사항: 
{external_data_str}
- [RAG 웹 검색 참조] 인터넷(블로그 등) 전문가 의견 요약:
{expert_opinions}
"""

        prompt_file_path = os.path.join(os.path.dirname(__file__), "prompts", "deep_research_prompt.md")
        try:
            with open(prompt_file_path, "r", encoding="utf-8") as pf:
                prompt = pf.read()
        except FileNotFoundError:
            raise Exception("프롬프트 파일을 찾을 수 없습니다: " + prompt_file_path)

        prompt = prompt.replace("{gongmae_instructions}", gongmae_instructions)
        prompt = prompt.replace("{current_year}", str(current_year))
        prompt = prompt.replace("{case_number}", str(case_number))
        prompt = prompt.replace("{address}", str(address))
        prompt = prompt.replace("{property_type}", str(property_type))
        prompt = prompt.replace("{appraised_value}", str(appraised_value))
        prompt = prompt.replace("{minimum_value}", str(minimum_value))
        prompt = prompt.replace("{auction_date}", str(auction_date))
        prompt = prompt.replace("{approval_date}", str(approval_date))
        prompt = prompt.replace("{land_area}", str(land_area))
        prompt = prompt.replace("{building_area}", str(building_area))
        prompt = prompt.replace("{risks}", str(risks))
        prompt = prompt.replace("{precautions}", str(precautions))
        prompt = prompt.replace("{tenant_warning}", str(tenant_warning))
        prompt = prompt.replace("{suspended_warning}", str(suspended_warning))
        prompt = prompt.replace("{ended_warning}", str(ended_warning))
        prompt = prompt.replace("{regulated_str}", str(regulated_str))
        prompt = prompt.replace("{house_count}", str(house_count))
        prompt = prompt.replace("{investor_type}", str(investor_type))
        prompt = prompt.replace("{investment_duration}", str(investment_duration))
        prompt = prompt.replace("{target_return}", str(target_return))
        prompt = prompt.replace("{status}", str(status))
        prompt = prompt.replace("{is_ended}", str(is_ended))
        prompt = prompt.replace("{final_date}", str(final_date))
        prompt = prompt.replace("{final_result}", str(final_result))
        prompt = prompt.replace("{history_str}", str(history_str))
        prompt = prompt.replace("{tenants_str}", str(tenants_str))
        prompt = prompt.replace("{pdf_context}", str(pdf_context))
        
        prompt += "\n\n**[중요 지시사항]: 응답은 반드시 '# 1. 요약'으로 시작해야 하며, 1번부터 10번까지의 목차를 빠짐없이 순서대로 작성하세요. 절대 중간 목차부터 시작하지 마세요.**\n"
        last_err_msg = ""
        for current_api_key in api_keys:
            try:
                genai.configure(api_key=current_api_key)
                model = genai.GenerativeModel('gemini-3.6-flash')
                response = model.generate_content([prompt])
                return response.text
            except Exception as e:
                err_msg = str(e)
                if "429" in err_msg:
                    last_err_msg = "구글 Gemini API 무료 할당량(요청 수 제한)을 초과했습니다."
                    continue
                elif "403" in err_msg and "denied access" in err_msg.lower():
                    last_err_msg = "Google Gemini API 키가 차단되었거나 권한이 거부되었습니다 (403 Forbidden)."
                    continue
                raise Exception(f"API 호출 오류: {err_msg}")
                
        raise Exception(last_err_msg or "모든 API 키에 대해 호출이 실패했습니다. (할당량 초과 또는 권한 문제)")
    except Exception as e:
        return f"⚠️ 중첩 분석 중 오류 발생: {str(e)}"

