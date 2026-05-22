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
    
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "⚠️ Gemini API 키가 설정되지 않아 심층 분석을 건너뛰었습니다."
    
    if not api_key.startswith("AIzaSy"):
        return f"⚠️ 유효하지 않은 Gemini API 키 형식입니다: {api_key[:10]}..."

    try:
        genai.configure(api_key=api_key)
        # Use stable gemini-2.5-flash for high-speed premium deep research
        model = genai.GenerativeModel('gemini-2.5-flash')
        
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
        
        property_type = data.get('property_type', '주택')
        house_count = data.get('house_count', '1주택')
        investor_type = data.get('investor_type', '개인')
        investment_duration = data.get('investment_duration', '단기(6개월)')
        target_return = data.get('target_return', '20')
        is_regulated = data.get('is_regulated_area', False)
        has_tenant = data.get('has_tenant', True)
        
        regulated_str = "조정대상지역" if str(is_regulated).lower() == 'true' else "비조정대상지역"

        tenant_warning = ""
        if not has_tenant:
            tenant_warning = "\n\n**[초강력 경고: 임차인 없음]**\n본 경매 물건은 법원 현황조사 결과 **임차인이 전혀 없는 물건**으로 확인되었습니다. 따라서 권리분석, 대항력, 인수 보증금, 가장임차인, 명도(세입자 퇴거) 등 **임차인과 관련된 그 어떠한 내용이나 단어도 보고서 전체에서 일절 언급하지 마십시오.** (임차인 관련 항목은 아예 지워버리세요.)\n"
        
        # 법원 서류 열람 중지 대응 안내 문구 생성
        viewing_suspended = data.get("viewing_suspended", False)
        suspended_docs = data.get("suspended_documents", [])
        
        suspended_warning = ""
        if viewing_suspended:
            suspended_warning = f"\n\n**[중요: 법원 서류 열람 중지 상태]**\n본 경매 물건은 현재 법원에서 서류({', '.join(suspended_docs) if suspended_docs else '등기부등본, 물건명세서 등'}) 열람을 중지/제한한 상태입니다. 따라서 **'1. 요약' 및 '2. 기본정보', '4. 권리분석'의 가장 첫 머리에 반드시 '본 사건은 현재 법원 서류 열람이 중지/제한된 상태'임을 알리는 문구를 진하고 명확하게 표시**하고, 마이옥션에 등재된 1차 정보 및 정밀 수집된 임차인 현황 데이터를 근거로 삼아 최선의 권리분석 및 리스크 진단을 완수하십시오.\n"

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
            if viewing_suspended:
                pdf_context = f"⚠️ [법원 서류 열람 중지 안내]\n본 사건은 현재 법원 서류 열람이 중지/제한된 상태입니다 (열람 중지 서류: {', '.join(suspended_docs) if suspended_docs else '전체'}).\n따라서 마이옥션에 등재된 1차 정보 및 정밀 수집된 임차인 현황 데이터를 기반으로 분석을 수행하십시오."
            else:
                pdf_context = data.get('pdf_text', '첨부된 PDF 텍스트가 없습니다. 기본 스크래핑 정보만으로 분석합니다.')

        # 구조화된 임차인 정보 포맷팅
        tenants_list = data.get("tenants", [])
        tenant_comments_list = data.get("tenant_comments", [])
        
        tenants_str = ""
        if tenants_list:
            tenants_str += "### [정밀 수집된 임차인 현황]\n"
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
        
        gongmae_instructions = ""
        if is_gongmae:
            gongmae_instructions = """
**[공매(온비드) 특화 권리분석 지침]**
본 건은 법원 경매가 아닌 한국자산관리공사(KAMCO) 주관의 **'공매(압류재산)'** 물건입니다. 따라서 다음 사항을 반드시 권리분석에 포함시키십시오.
1) **조세채권 및 체납액 우선변제권**: 제공된 [첨부 PDF 데이터(공매재산명세서 등)]에서 '법정기일'을 확인하고, 임차인의 '전입일자/확정일자'와 비교하여 조세채권이 우선하는지(당해세 포함) 반드시 분석하십시오.
2) **배당(분배) 요구**: 공매에서는 배당요구를 '배분요구'라고 합니다. 임차인이 배분요구 종기일 내에 적법하게 배분요구를 했는지 명시하십시오.
3) **인수 보증금 리스크**: 조세채권(법정기일)이 임차인의 대항력/확정일자보다 빠를 경우, 낙찰 대금에서 세금이 먼저 배분되어 임차인의 보증금이 전액 배분되지 않을 수 있습니다. 이 경우 남은 보증금은 낙찰자가 전액 인수해야 하므로 이를 매우 강력하게 경고하고 예상 인수 금액을 계산하십시오.
4) 공매의 특성상 명도소송(인도명령 불가)이 필요할 수 있음을 출구전략에 명시하십시오.
"""

        import datetime
        current_year = datetime.datetime.now().year

        prompt = f"""
당신은 20년 경력의 실전 경매/공매 전문 투자자이자 최고 수준의 AI 애널리스트입니다.
아래 제공된 [경매/공매 물건 정보] 및 [첨부 PDF 데이터]를 바탕으로, 지시된 '9단계 목차'와 '계산 공식'에 맞추어 완벽한 심층 분석 보고서를 마크다운 형식으로 작성하십시오.
{gongmae_instructions}

### [경매/공매 물건 정보]
- 사건번호: {case_number}
- 물건소재지: {address}
- 부동산종류: {property_type}
- 감정가: {appraised_value}원
- 최저가: {minimum_value}원
- 매각기일: {auction_date}
- 사용승인일자: {approval_date}
- 대지면적: {land_area}
- 전용면적(건물면적): {building_area}
- 식별된 리스크(키워드): {risks}
- 매각물건명세서(공매재산명세서) 주의사항/특수권리 원문:
{precautions}{tenant_warning}{suspended_warning}
- 규제지역 여부: {regulated_str}
- 투자자 조건: {house_count}, {investor_type}, {investment_duration} 매도 전략, 목표수익률 연 {target_return}%

### [정밀 수집된 임차인 및 점유 현황]
{tenants_str}

### [첨부 PDF 데이터 (매각물건명세서/감정평가서 등)]
{pdf_context}

### [분석 보고서 작성 지침 - 반드시 아래 10개 목차를 빠짐없이 준수할 것]
(시세 및 수익성 현황, 입지분석 등 어느 항목도 누락하거나 병합하지 마십시오.)

# 1. 요약
- 핵심 리스크와 투자 매력도를 5줄 이내로 간결하게 브리핑.
- 마지막 줄에 투자 여부를 [Go] 또는 [Stop] 으로 명확히 기재할 것.

# 2. 기본정보
- 사건번호, 주소지, 대지평수, 건물평수, 감정가, 최저가, 매각기일, 사용승인일자 기재. (입력된 사용승인일자가 '알 수 없음'인 경우, 반드시 첨부된 PDF 데이터를 읽고 연/월을 추정하여 기재할 것)
- 2회 이상 유찰 시 그 유찰 사유, 미납 사유, 변경 사유 등을 추정하여 기재.
- 식별된 리스크 정보에 'HUG 대항력포기'가 포함되어 있거나, 첨부 문서상 주택도시보증공사(또는 주식도시보증공사)의 대항력 포기 확약서 등이 존재하는지 반드시 확인하고, 그 여부를 기재할 것.

# 3. 물리적현황
- 노후도 산출 (현재 연도({current_year}년) - 사용승인연도)
- 노후도에 따른 수리비 예상 (공식 적용: 10년이하 20%, 25년이하 50%, 35년이하 75%, 35년이상 100% * 평당수리비 150만원). 이를 기반으로 총 수리비 산출.
- 미납관리비: 현재 수준 공용관리비 추정치 기재.
- 위반건축물 여부: 건축물대장 및 현황조사 기준 이행강제금 추정치.

# 4. 권리분석
- 경매개시결정등기 이후 신고/설정된 권리 유무 (유치권, 임차권 등기 등).
- 말소기준권리 파악 및 그보다 앞서 인수해야 할 선순위 금액 분석. (단, 매각물건명세서/현황조사서 상 임차인이 없는 물건의 경우, 대항력이나 인수 보증금에 관한 불필요한 언급은 생략할 것)
- 매각물건명세서(공매재산명세서)의 '비고(주의사항)' 란을 필히 체크하여 특수권리가 있는지 확인하고 기재할 것.
- 인수 권리 및 임차인 보증금 분석: 
  1) 임차인의 대항력 유무를 파악하고, 배당요구일이 배당요구종기일 이내인지(적법한 배당요구인지) 확인하십시오.
  2) 임차인이 적법하게 배당요구를 한 경우, 예상 낙찰금액이 임차인의 보증금을 상회한다면 (경매비용과 당해세 등이 없다는 가정 하에) 낙찰자가 추가로 인수할 보증금이 없다는 점을 논리적으로 계산하여 분석에 반영하십시오.
  3) 전세권 등 기타 인수되는 권리가 있다면 낙찰가 대비 정확한 인수금액을 계산하십시오.
- 첨부된 **매각물건명세서(또는 공매재산명세서)** 및 관련 PDF 문서를 심층 분석하여 다음의 특수 권리/조건들의 **유무(표시 여부)**를 반드시 파악하십시오:
  1) 유치권
  2) 법정지상권 (관습법상 법정지상권 포함)
  3) 건물만 매각 / 토지만 매각
  4) HUG(주택도시보증공사) 대항력 포기
  5) 토지별도등기 (토지에 지상권, 저당권 등)
  6) 대지권 미등기
  7) 지분경매
- 위 특수 권리/조건 중 **해당 사항이 있는 경우**, 단순히 존재 유무만 나열하지 말고 다음 사항들을 보고서(권리분석 섹션)에 **반드시** 추가하십시오:
  * **성�        try:
            # 로컬 PDF 텍스트 추출 완료 및 프롬프트 주입으로 File API 업로드 필요 없음 (속도 3배 개선)
            response = model.generate_content([prompt])
            return response.text고, 지료 청구나 지분 인수/공유물 분할 소송 등 실질적인 출구 전략을 제시할 것.
- 다음 항목들에 대해 [O] 또는 [X] 로 명확히 표시하고 판단 이유를 덧붙일 것:
  * 유치권 존재 및 성립 여부 [ ]
  * 법정지상권 존재 및 성립 여부 [ ]
  * 토지별도등기 여부 [ ]
  * 대지권미등기 여부 [ ]
  * 특수매각 (건물만/토지만/지분경매) 여부 [ ]
  * HUG 대항력 포기 여부 [ ]
  * 가장임차인 의심 여부 [ ] (단, 임차인이 없는 물건이면 이 항목 삭제)

# 5. 시세 및 수익성 현황
- 최근 1년간 반경 1km 내 유사평수, 유사건축년도, 유사층수의 거래건수 3건 이상을 비교하는 시세비교 표를 작성.
- 해당 부동산의 예상 시세는 비교된 '전용 평당가'에 해당 물건의 '건물면적(전용면적)'을 곱하여 산출하는 공식과 결과값(코멘트)을 명시.
- **수익률 표 작성**: 인수금액, 세금, 기타비용, 이자비용, 중개보수, 수리비 등 총 비용을 감안하여, '현재 최저가' 기준 수익률과 여기서 '10%씩 Up한 입찰가' 기준의 단계별 수익률(3단계)을 시뮬레이션 표로 작성할 것.

# 6. 입지분석
- 지하철 역과의 거리, 초/중/고 학교 거리.
- 반경 5km 내 개발계획, 도로 건설, 지하철(철도)역 및 노선의 사업명 및 착공/완공 시기 조사 (웹 지식 활용).
- **입지 기반 추천업종:** 해당 물건의 거주인구, 직장인구, 유동인구 밀집도 및 배후수요 성격에 가장 부합하는 권장 업종 3~5개와 그 구체적인 추천 사유(입지 활용 제안)를 명확히 작성하십시오.

# 7. 추천입찰가
- {investment_duration} 내 {target_return}%의 수익률을 목표로 할 때, 역산하여 도출한 추천 입찰가 기재 및 산출 근거 서술.

# 8. 출구전략
- 3년 이상 보유 임대전략 vs 6개월 내 단기매도 전략 중 대상 물건에 가장 유리한 것을 선택.
- 유리한 이유와 실행에 옮기기 위한 구체적인 액션 플랜(명도 후 인테리어 방향, 매물 등록 시기 등) 제시.
- **물건종류가 '아파트형공장' 또는 '지식산업센터'인 경우:** 원칙적으로 낙찰 후 임차인 자격조건은 '기업주(사업자)'에 해당함을 명시할 것. 단, 1층이나 지하 1층에 위치하고 용도가 '지원시설' 또는 '근린상가'인 경우 일반 상가로 간주하여 임대가 가능할 수 있음을 분석할 것. 만약 입주 자격(기업주 등)을 충족하지 못하거나 불법 용도로 임대/사용할 경우, 적발 시 6개월 내 강제매각 조치를 당할 수 있다는 치명적 리스크를 임대 전략 및 단기매도 전략에 반드시 포함하여 경고할 것.

# 9. 대출절세전략
- 현재 투자 조건({house_count}, {investor_type}, {regulated_str})에 따른 세금 시뮬레이션 (2025.10.16 기준):
  * 취득세: 1주택 1~3%, 2주택 (조정지역 8%, 비조정 1~3%), 3주택 이상 (조정지역 12%). 매매사업자도 주택 취득 시 개인과 동일하며 2주택부터 중과. (주의: 본 건이 오피스텔인 경우, 주택 수 및 조정지역 여부와 무관하게 매입 시 취득세가 4.6%임을 명시할 것)
  * 양도소득세: 본세와 지방소득세(본세의 10%)를 합산하여 적용할 것. 개인이 단기매도 시 1년 미만은 77%, 2년 미만은 66% 적용. 개인 1세대 1주택은 조정지역 시 2년 보유+2년 거주 필수. 다주택자는 조정지역 양도 시 기본세율 + 20~30%p 중과 및 장기보유특별공제 배제. (주의: 본 건이 오피스텔인 경우, 전용면적 40평방미터 이하, 공시지가 1억 원 이하, 매각 시 6억 원 이하의 조건을 충족하면 다주택자라도 양도세 중과세가 배제된다는 점을 반드시 추가 기재할 것)
- 대출가능금액 산출: 
  * 주택의 경우 조정지역 LTV 40% 이하, 비규제지역 LTV 70% 이하 (DSR 40% 공통 적용).
  * 금액별 대출 한도 (15억 이하 최대 6억, 15~25억 4억, 25억 이상 2억)를 반영하여 실제 대출 한도 금액 제시.

# 10. 최종 결론
- 본 경매 물건에 대한 종합적인 투자 판단을 반드시 [투자 판정: GO], [투자 판정: Neutral], [투자 판정: Danger] 중 하나로 선택하여 이 섹션의 가장 첫 줄에 명시할 것.
- 투자를 진행하거나 보류/포기해야 하는 **핵심 사유 3가지**를 구체적이고 논리적으로 서술.
- 예상되는 가장 큰 리스크와 그에 대한 대비책을 종합적으로 요약.

---
모든 분석은 전문가답고 확신에 찬 어조로 작성하되, 금액 단위는 모두 읽기 쉽게 '00만 원' 또는 '00억 00만 원' 형태로 표기해 주십시오. (예: 50,000,000원 -> 5,000만 원)
마지막에는 반드시 아래 형태의 JSON 블록을 하나만 정확히 넣어 프론트엔드가 차트를 그릴 수 있게 해주세요. (값은 모두 int형 숫자만 기재, 비율은 소수점 허용)

```json
{{
  "estimated_price": 500000000,
  "estimated_takeover": 0,
  "margin_rate": 20.5,
  "target_bid_price": 400000000,
  "chart_data": {{
    "conservative_sale_price": 500000000,
    "target_profit": 50000000,
    "capital_gains_tax": 30000000,
    "capex_and_eviction": 15000000,
    "interest_and_acq_tax": 15000000,
    "max_bidding_price": 390000000,
    "short_term_tax_rate": 30,
    "long_term_tax_rate": 20
  }}
}}
```
"""
        try:
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
                        while uploaded_file.state.name == 'PROCESSING':
                            print(f"{pdf_path} 처리 대기 중...")
                            time.sleep(2)
                            uploaded_file = genai.get_file(uploaded_file.name)
                            
                        uploaded_files.append(uploaded_file)
                        contents.append(uploaded_file)
                        print(f"업로드 완료: {uploaded_file.name}")
                    except Exception as e:
                        print(f"PDF 업로드 실패 ({pdf_path}): {e}")

            response = model.generate_content(contents)
            
            # 분석 후 업로드된 파일 정리 (저장공간 관리)
            for uf in uploaded_files:
                try:
                    genai.delete_file(uf.name)
                    print(f"정리 완료: {uf.name}")
                except Exception as e:
                    print(f"파일 정리 실패 ({uf.name}): {e}")
                    
            return response.text
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg:
                raise Exception("구글 Gemini API 무료 할당량(요청 수 제한)을 초과했습니다. 잠시 후 [분석 시작] 버튼을 다시 눌러주세요. 계속 발생 시 Google AI Studio에서 카드 등록이 필요합니다.")
            raise Exception(f"API 호출 오류: {err_msg}")
                    
    except Exception as e:
        return f"⚠️ 심층 분석 중 오류 발생: {str(e)}"
