file_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\backend\ai_analyzer.py"

for enc in ['cp949', 'euc-kr', 'utf-8', 'utf-8-sig']:
    try:
        with open(file_path, "r", encoding=enc) as f:
            content = f.read()
        print(f"SUCCESSfully read with {enc}!")
        
        target = """### [첨부 PDF 데이터 (매각물건명세서/감정평가서 등)]
{pdf_context}

### [분석 보고서 작성 지침 - 반드시 아래 10개 목차를 빠짐없이 준수할 것]
(시세 및 수익성 현황, 입지분석 등 어느 항목도 누락하거나 병합하지 마십시오.)"""

        replacement = """### [첨부 PDF 데이터 (매각물건명세서/감정평가서 등)]
{pdf_context}

### [선순위 인수보증금 감안 입찰가 계산 절대 법칙 (초강력 준수 지침)]
대항력이 있는 임차인의 보증금 중 낙찰자가 배당으로 해결하지 못하고 **인수해야 하는 선순위 인수 보증금(인수금액)**이 존재할 경우, 모든 보고서 서술과 수익률 시뮬레이션 및 최종추천입찰가 계산 시 다음 수학적 규칙을 **반드시 100% 엄격하게 준수하십시오**:
1. **추천 입찰가 계산 공식**:
   `추천 입찰가(target_bid_price 및 max_bidding_price) = 예상 매매가(또는 감정가) - 목표 수익 - 모든 비용(취득세, 중개보수, 수리비, 대출이자 등) - 선순위 인수금액`
   이 공식을 무조건 적용하십시오. 선순위 인수금액이 누락되거나 입찰가 계산 시 차감되지 않으면 절대 안 됩니다!
2. **입찰가 0원 이하/음수 처리 규칙**:
   인수해야 할 보증금이 예상 매매가보다 크거나, 위 공식에 따른 추천 입찰가가 0원 이하(음수)로 산출되는 경우, **추천 입찰가(target_bid_price, max_bidding_price)는 절대로 양수(+)의 값으로 제안하지 마십시오.** 계산 결과를 그대로 음수 또는 0원(예: -1억 5,000만 원, 또는 0원)으로 확실하게 표기하십시오. 그리고 "본 건은 인수금액이 시세 대비 너무 과도하여 입찰가가 제로(0원)에도 미치지 못하는 초고위험 물건이므로 절대로 입찰해서는 안 되며, 입찰할 경우 막대한 손실을 입게 됩니다"라고 **강력하게 입찰 포기를 경고**하십시오.
3. **최종 결론 매칭**:
   인수 금액이 과도해 계산된 입찰가가 0원 이하(음수)가 나오는 경우, '10. 최종 결론' 섹션에서는 무조건 **[투자 판정: Danger]**로 규정하고, 추천입찰가와 시뮬레이션 표에도 이를 고스란히 영 이하 또는 마이너스 가격 및 극심한 손실률로 일관되게 표현하십시오. JSON 데이터의 `target_bid_price` 및 `max_bidding_price` 또한 반드시 0원(또는 음수)으로 입력해야 합니다.

### [분석 보고서 작성 지침 - 반드시 아래 10개 목차를 빠짐없이 준수할 것]
(시세 및 수익성 현황, 입지분석 등 어느 항목도 누락하거나 병합하지 마십시오.)"""

        content_lf = content.replace("\r\n", "\n")
        target_lf = target.replace("\r\n", "\n")
        replacement_lf = replacement.replace("\r\n", "\n")

        if target_lf in content_lf:
            new_content = content_lf.replace(target_lf, replacement_lf)
            # Write back in the same encoding
            with open(file_path, "w", encoding=enc) as f:
                f.write(new_content)
            print(f"SUCCESSFULLY UPDATED with encoding {enc}!")
            break
        else:
            # Let's check why target not found (could be minor character diffs)
            print(f"Target not found with encoding {enc}. Checking index of '첨부 PDF 데이터'...")
            idx = content.find("첨부 PDF 데이터")
            print(f"Index of '첨부 PDF 데이터': {idx}")
            
    except Exception as e:
        print(f"Failed to read/update with {enc}: {e}")
