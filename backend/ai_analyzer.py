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
        house_count = data.get('house_count', '1주택')
        investor_type = data.get('investor_type', '개인')
        investment_duration = data.get('investment_duration', '단기(6개월)')
        target_return = data.get('target_return', '20')
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
아래 제공된 [경매/공매 물건 정보], [마이옥션 상세 데이터], [첨부 PDF 데이터]를 바탕으로, 지시된 '10개 목차'와 '계산 공식'에 맞추어 완벽한 심층 분석 보고서를 마크다운 형식으로 작성하십시오.

⚠️ **[주의사항 - 서류 열람 관련 문구 절대 금지]**
- 보고서 작성 시 "현재 법원 서류 열람이 중지/제한된 상태입니다." 또는 이와 유사한 서류 미비/열람 제한 관련 표현은 **일절 언급하거나 넣지 마십시오.** 마이옥션에서 수집한 PDF 및 상세 기본 정보를 100% 신뢰하여 완벽하고 명확한 권리분석 보고서를 작성하십시오.

{gongmae_instructions}

### [MCP 도구 연동 지침 - korean-law & archhub 필수 참조]
1) **`korean-law` MCP (법률 및 소송사건 참조)**:
   - 권리분석 중 유치권 성립여부, 법정지상권, 인도명령/명도소송, 배당이의, 공유물분할 소송, 주택/상가임대차보호법 해석 등 **소송 사건이나 법률적 문제가 있는 경우**, `korean-law` MCP 도구를 참조하여 관련 법령 조항(민법, 민사집행법 등) 및 대법원 판례 근거에 기초하여 법적 승소 가능성 및 리스크 대응책을 서술하십시오.

2) **`archhub` MCP (건축물대장 및 인허가 정보 참조)**:
   - 해당 부동산의 기본 정보 및 물리적 현황 분석 시, `archhub` MCP를 참조하여 해당 부동산의 **표제부/전유부 건축물대장 상세 내역, 위반건축물 지정 사유 및 이행강제금 관련 인허가 정보, 건축물 주용도, 착공일자, 사용승인일자, 구조/층수 등 모든 상세 건축 정보를 참조하여 보고서에 정확히 반영**하십시오.

### [소액임차인 최우선변제 분석 정밀 지침 - 필수 반영]
임차인 분석 시 **소액임차인 해당 여부 및 최우선변제금**은 **반드시 무조건 "말소기준권리의 설정일자" 당시의 법령 기준표를 기준으로 판단**해야 합니다. (임차인의 전입일이나 현재 일자를 기준으로 잡으면 절대 안 됨!)

1) **주택 소액임차인 최우선변제 기준 (말소기준권리 설정일자 기준)**:
   - 2023.02.14 이후: 서울(1억6천5백이하 -> 5500만원), 과밀억제(1억4천5백이하 -> 4800만원), 용인/화성/세종/김포/광역(8500이하 -> 2800만원), 기타(7500이하 -> 2500만원)
   - 2021.05.11 이후: 서울(1억5천이하 -> 5500만원), 과밀억제(1억3천이하 -> 4300만원), 광역/안산/광주/파주/이천/평택(7000이하 -> 2300만원), 기타(6000이하 -> 2000만원)
   - 2018.09.18 이후: 서울(1억1천이하 -> 3700만원), 과밀억제(1억이하 -> 3400만원), 세종/용인/화성/광역/안산/김포/광주/파주(6000이하 -> 2000만원), 기타(5000이하 -> 1700만원)
   - 2016.03.31 이후: 서울(1억이하 -> 3400만원), 과밀억제(8000이하 -> 2700만원), 광역/김포/안산/용인/광주/세종(6000이하 -> 2000만원), 기타(5000이하 -> 1700만원)
   - 2014.01.01 이후: 서울(9500이하 -> 3200만원), 과밀억제(8000이하 -> 2700만원), 광역/김포/안산/용인/광주(6000이하 -> 2000만원), 기타(4500이하 -> 1500만원)
   - 2010.07.26 이후: 서울(7500이하 -> 2500만원), 과밀억제(6500이하 -> 2200만원), 광역/김포/안산/용인/광주(5500이하 -> 1900만원), 기타(4000이하 -> 1400만원)
   - 2008.08.21 이후: 서울(6000이하 -> 2000만원), 수도권과밀(5000이하 -> 1700만원), 광역(5000이하 -> 1700만원), 기타(4000이하 -> 1400만원)
   - 2001.09.15 이후: 서울(4000이하 -> 1600만원), 과밀억제(3500이하 -> 1400만원), 광역(3500이하 -> 1400만원), 기타(3000이하 -> 1200만원)

2) **상가 소액임차인 최우선변제 기준 (말소기준권리 설정일자 및 환산보증금 기준)**:
   * **환산보증금 공식**: `보증금 + (월세 × 100)` (환산보증금이 상가임대차보호법 적용 범위 내에 있어야 보호받음)
   - 2019.04.02 이후: 서울(환산 9억이하, 소액보증금 6500만이하 -> 최우선 2200만원), 과밀/부산(환산 6억9천이하, 소액 5500만이하 -> 최우선 1900만원), 광역/세종/파주/화성 등(환산 5억4천이하, 소액 3800만이하 -> 최우선 1300만원), 기타(환산 3억7천이하, 소액 3000만이하 -> 최우선 1000만원)
   - 2018.01.26 ~ 2019.04.01: 서울(환산 6억1천이하, 소액 6500만이하 -> 2200만원), 과밀/부산(환산 5억이하, 소액 5500만이하 -> 1900만원), 광역 등(환산 3억9천이하, 소액 3800만이하 -> 1300만원), 기타(환산 2억7천이하, 소액 3000만이하 -> 1000만원)
   - 2014.01.01 ~ 2018.01.25: 서울(환산 4억이하, 소액 6500만이하 -> 2200만원), 과밀(환산 3억이하, 소액 5500만이하 -> 1900만원), 광역 등(환산 2억4천이하, 소액 3800만이하 -> 1300만원), 기타(환산 1억8천이하, 소액 3000만이하 -> 1000만원)
   - 2010.07.26 ~ 2013.12.31: 서울(환산 3억이하, 소액 5000만이하 -> 1500만원), 과밀(환산 2억5천이하, 소액 4500만이하 -> 1350만원), 광역 등(환산 1억8천이하, 소액 3000만이하 -> 900만원), 기타(환산 1억5천이하, 소액 2500만이하 -> 7500천원)
   - 2008.08.21 ~ 2010.07.25: 서울(환산 2억6천이하, 소액 4500만이하 -> 1350만원), 과밀(환산 2억1천이하, 소액 3900만이하 -> 1170만원), 광역 등(환산 1억6천이하, 소액 3000만이하 -> 900만원), 기타(환산 1억5천이하, 소액 2500만이하 -> 7500천원)
   - 2002.11.01 ~ 2008.08.20: 서울(환산 2억4천이하, 소액 4500만이하 -> 1350만원), 과밀(환산 1억9천이하, 소액 3900만이하 -> 1170만원), 광역 등(환산 1억5천이하, 소액 3000만이하 -> 900만원), 기타(환산 1억4천이하, 소액 2500만이하 -> 7500천원)

3) **임차인 분석 시 선순위/후순위 소액임차인 처리 법칙**:
   - **선순위임차인이면서 소액임차인인 경우**: 최우선변제금만큼은 배당절차에서 최우선으로 변제받고, 배당받지 못한 남은 잔여 보증금은 선순위 대항력에 의해 **낙찰자가 전액 인수**함을 논리적으로 계산하여 밝히십시오.
   - **후순위임차인이면서 소액임차인인 경우**: 말소기준권리보다 전입/확정이 늦더라도, 소액임차인 요건을 충족하고 적법한 배당요구를 했다면 최우선변제 범위 내 금액을 최우선 배당받고, 남은 보증금은 소멸되므로 인수금이 발생하지 않는 구조임을 서술하십시오.

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
{precautions}{tenant_warning}{suspended_warning}{ended_warning}
- 규제지역 여부: {regulated_str}
- 투자자 조건: {house_count}, {investor_type}, {investment_duration} 매도 전략, 목표수익률 연 {target_return}%
- 사건 진행 상태: {status} (종결 여부: {is_ended}, 최종 날짜: {final_date}, 최종 결과: {final_result})
- 진행 이력 (기일내역):
{history_str}

### [정밀 수집된 임차인 및 점유 현황]
{tenants_str}

### [첨부 PDF 데이터 (매각물건명세서/감정평가서 등)]
{pdf_context}

### [분석 보고서 작성 지침 - 반드시 아래 10개 목차를 빠짐없이 준수할 것]
(시세 및 수익성 현황, 입지분석 등 어느 항목도 누락하거나 병합하지 마십시오.)

# 1. 요약
- 핵심 리스크와 투자 매력도를 5줄 이내로 간결하게 브리핑.
- 마지막 줄에 투자 여부를 [Go] 또는 [Stop] 으로 명확히 기재할 것. (만약 이미 과거/종결된 사건이라면, 투자 여부 기재 대신 '본 사건은 [최종날짜]에 [최종결과]로 종결된 과거 사건입니다.' 형식으로 요약에 한 줄 명시할 것.)

# 2. 기본정보
- 사건번호, 주소지, 대지평수, 건물평수, 감정가, 최저가, 매각기일, 사용승인일자 기재. (입력된 사용승인일자가 '알 수 없음'인 경우, 반드시 첨부된 PDF 데이터를 읽고 연/월을 추정하여 기재할 것)
- 2회 이상 유찰 시 그 유찰 사유, 미납 사유, 변경 사유 등을 추정하여 기재.
- 식별된 리스크 정보에 'HUG 대항력포기'가 포함되어 있거나, 첨부 문서상 주택도시보증공사(또는 주식도시보증공사)의 대항력 포기 확약서 등이 존재하는지 반드시 확인하고, 그 여부를 기재할 것.

# 3. 물리적현황
- 노후도 산출 (현재 연도({current_year}년) - 사용승인연도)
- 노후도에 따른 수리비 예상 (공식 적용: 10년이하 20%, 25년이하 50%, 35년이하 75%, 35년이상 100% * 평당수리비 150만원). 이를 기반으로 총 수리비 산출.
- 미납관리비: 현재 수준 공용관리비 추정치 기재.
- 위반건축물 여부: 건축물대장 및 현황조사 기준 이행강제금 추정치.
- 감정평가서 상의 물리적 상세 현황 기재 (제공된 첨부 PDF 감정평가서 등에서 상세히 확인하여 반드시 다음 각 항목을 개별 표시):
  * 방개수 (예: 방 3개)
  * 화장실 (예: 화장실 2개)
  * 거실기준 방향 (예: 남향, 동향 등)
  * 복도식, 계단식 구분 (예: 계단식 / 복도식 / 혼합식 등)
  * 엘리베이터유무 (예: 있음 / 없음)
  * 난방방식 (예: 개별난방 도시가스 등)

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
  * **성립 여부**: 유치권 성립 여부(점유 시점, 피담보채권 성립 시점), 법정지상권 성립 여부(토지/건물 소유자 동일성 여부 등) 분석 및 지료 청구나 지분 인수/공유물 분할 소송 등 실질적인 출구 전략을 제시할 것.
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
- 현재 투자 조건({house_count}, {investor_type}, {regulated_str})에 따른 세금 시뮬레이션:
  * 취득세:
    - [개인 & 매매사업자]: 1주택 1~3%, 2주택 (조정지역 8%, 비조정 1~3%), 3주택 이상 (조정지역 12%). 매매사업자도 주택 취득 시 개인과 동일하며 2주택부터 중과.
    - [법인]:
      1) **주택 매입 시**: 주택 수 및 규제지역 여부와 무관하게 **취득세 12% 중과** 적용.
      2) **일반 상가/토지 매입 시**: 기본 취득세 **4.6%** 적용.
      3) **과밀억제권역 내 설립 5년 이내 법인의 상가/부동산 매입 시**: **취득세 9.6% 중과** 적용 (과밀억제권역 범위: 서울특별시 전역, 인천광역시 일부, 경기도 성남·수원·고양·안양·부천·의정부·광명·군포·의왕·하남·구리, 남양주/시흥/파주 일부 등).
      4) **오피스텔 매입 시**: 주택 수 및 법인 여부와 무관하게 취득세 **4.6%** 적용.
  * 양도소득세 / 법인세 (본세와 지방소득세(본세의 10%)를 합산하여 적용):
    - [개인의 상가 및 토지]: 1년 내 매도 시 55% (지방세 포함 60.5%), 2년 내 매도 시 44% (지방세 포함 48.4%) 적용.
    - [개인의 주택 매매]: 1주택인 경우 양도가액 12억원 이하일 때 2년 이상 보유 시 비과세(조정지역은 2년 보유+2년 거주 필수). 다주택자는 6~45% (기본세율) 적용.
    - [매매사업자]: 6~45% (기본세율) 적용.
    - [법인]: 9~19% (기본 법인세율) 적용. 단, 주택 및 비사업용 토지 양도 시 법인세 기본세율에 **20% 추가 과세** (총 29~39%) 적용.
    - (주의: 본 건이 오피스텔인 경우, 전용면적 40평방미터 이하, 공시지가 1억 원 이하, 매각 시 6억 원 이하의 조건을 충족하면 다주택자라도 양도세 중과세가 배제된다는 점을 반드시 추가 기재할 것)
- 대출가능금액 산출: 
  * 개인 주택의 경우 조정지역 LTV 40% 이하, 비규제지역 LTV 70% 이하 (DSR 40% 공통 적용).
  * 법인의 경우: 가계대출 DSR 규제를 우회하여 법인 명의 사업자 대출(시설자금대출/운전자금대출) 활용 가능 여부 및 RTI(임대업이자상환비율) 조항을 검토하여 분석할 것.
  * 금액별 대출 한도 (15억 이하 최대 6억, 15~25억 4억, 25억 이상 2억)를 반영하여 실제 대출 한도 금액 제시.

# 10. 최종 결론
- 본 경매 물건에 대한 종합적인 투자 판단을 반드시 [투자 판정: GO], [투자 판정: Neutral], [투자 판정: Danger] 중 하나로 선택하여 이 섹션의 가장 첫 줄에 명시할 것. (단, 본 사건이 과거/종결된 사건일 경우에는 [투자 판정: 종결 (유찰)], [투자 판정: 종결 (낙찰)], [투자 판정: 종결 (변경)], [투자 판정: 종결 (취소/취하)] 등으로 표기하여 이미 종결된 과거 사건임을 명확히 드러낼 것.)
- 투자를 진행하거나 보류/포기해야 하는 **핵심 사유 3가지**를 구체적이고 논리적으로 서술. (과거/종결 사건인 경우 해당 결과를 맞이한 원인 분석을 포함하여 서술할 것.)
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
                raise Exception("구글 Gemini API 무료 할당량(요청 수 제한)을 초과했습니다. 잠시 후 다시 시도해주세요.")
            elif "403" in err_msg and "denied access" in err_msg.lower():
                raise Exception("Google Gemini API 키가 차단되었거나 권한이 거부되었습니다 (403 Forbidden). Google AI Studio에 로그인하여 계정 상태를 확인하고 새로운 API 키를 발급받아 .env 파일에 업데이트해 주세요.")
            raise Exception(f"API 호출 오류: {err_msg}")
                    
    except Exception as e:
        return f"⚠️ 심층 분석 중 오류 발생: {str(e)}"


def analyze_overlap_cases(items: list) -> str:
    """
    형광펜 중첩 베스트 3 물건에 대한 제미나이 2.5 Flash 기반 약식 권리분석 및 리스크/수익률 리포트 생성
    """
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path=env_path)
    
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "⚠️ Gemini API 키가 설정되지 않아 중첩 분석을 수행할 수 없습니다."
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
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

        prompt = f"""
당신은 20년 경력의 실전 경매 및 공매 전문 투자자입니다.
지도의 특정 구역에서 여러 개발 계획 레이어(택지지구, 재개발구역, 용도지역, 도시계획도로 등)가 중첩되는 '골든 존(Golden Zone)' 내의 중첩 물건 분석을 요청받았습니다.
제공된 중첩 물건 정보(최대 3개)를 바탕으로, 각 물건의 리스크와 사업성/수익률을 정밀 분석하고 전체 리스트에 대한 최종 추천 별점 평점을 매기는 리포트를 마크다운 형식으로 작성하십시오.

### [중첩 분석 대상 물건 정보]
{items_context}

### [리포트 작성 가이드라인 - 각 물건별 정밀 분석 필수 항목]
1. **서론**: 분석 대상 지역의 개발 호재(중첩된 개발 정보들)의 시너지 효과를 2-3줄로 요약하십시오.
2. **개별 물건 분석 (Best 3)**:
   - 각 물건별로 동일한 문구 템플릿 복붙을 절대 금하며, 데이터와 지식을 바탕으로 아래 **9가지 필수 항목**을 마크다운 리스트 형태로 빠짐없이 작성하십시오:
     * **1. 매각기일 및 주소**: 
     * **2. 감정평가현황 (최저가율)**: 감정가, 최저가, 감정가 대비 최저가율
     * **3. 건축년도, 평수, 층수, 지목**: 전용면적 및 대지면적(토지면적) 포함 (주어진 면적 데이터를 평수로 환산하여 기재)
     * **4. 권리분석 (선순위 인수금액 유무)**: 대항력 있는 선순위 임차인이나 유치권 등 인수해야 할 선순위 금액 유무 (없다면 '인수금액 없음' 명시)
     * **5. 조세채권 및 당해세 유무**: 공매/경매 특성상 조세채권(당해세) 배분 리스크 서술
     * **6. 반경 5km 내 개발계획 명칭**: 중첩된 레이어 데이터를 바탕으로 구체적인 개발계획 수혜 서술
     * **7. 아파트 세대수 및 역세권 유무**: 인근 지하철역 거리 기반 역세권 여부 및 아파트의 경우 예상 세대수 규모 (아파트가 아니면 해당 용도 기재)
     * **8. 출구 전략 (단기매도 vs 임대전략)**: 둘 중 대상 물건에 더 유리한 전략 선택 및 구체적 이유 (수익률 시뮬레이션 포함)
     * **9. 위험요소 (리스크)**: 투자를 저해할 수 있는 치명적 단점이나 리스크 1~2개
   - 경매 물건은 **마이옥션**, 공매 물건은 **온비드** 데이터를 기초로 분석했다는 점을 명시하십시오.
3. **종합 추천 평점 (별 5개 평점 부여)**:
   - 베스트 3 물건 전체에 대한 최종 투자 매력도를 종합 평가하여 5성급 평점(예: ⭐⭐⭐⭐⭐)을 부여하고, 그 사유를 명시하십시오.
4. **연동 안내**:
   - "상세 권리분석을 원하시면 물건 번호 또는 사건번호를 클릭하여 정밀 권리분석 보고서를 로드하십시오." 라는 안내 문구를 하단에 포함시키십시오.

모든 금액은 읽기 쉽게 '00만 원' 또는 '00억 00만 원' 형태로 작성해주십시오.
어조는 투자 전문가처럼 단호하고 설득력 있게 작성해주십시오.
"""

        response = model.generate_content([prompt])
        return response.text
    except Exception as e:
        return f"⚠️ 중첩 분석 중 오류 발생: {str(e)}"

