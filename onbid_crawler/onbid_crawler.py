import requests
import pandas as pd
import datetime
import os
import time
from openpyxl.utils import get_column_letter

from config import ONBID_CONFIG
from onbid_canceled_crawler import collect_canceled_and_withdrawn_records

# 동적 설정 레지스트리 참조
SERVICE_KEY = ONBID_CONFIG["rlst_list_service_key"]
API_URL = ONBID_CONFIG["rlst_list_url"]
TARGET_REGIONS = ONBID_CONFIG["target_regions"]

# 출력 컬럼 정의
COLUMNS_MAP = {
    "pvctTrgtYn_text": "계약상태",
    "cltrMngNo": "물건관리번호",
    "pbctNo": "공매번호",
    "prptDivNm": "재산유형명",
    "cltrUsgMclsCtgrNm": "용도(중분류)",
    "cltrUsgSclsCtgrNm": "용도(소분류)",
    "onbidCltrNm": "물건명",
    "lctnSdnm": "시도",
    "lctnSggnm": "시군구",
    "lctnEmdNm": "읍면동",
    "cltrRadr": "상세주소",
    "apslEvlAmt": "감정평가금액",
    "lowstBidPrcIndctCont": "최저입찰가격",
    "cltrBidBgngDt": "입찰시작일시",
    "cltrBidEndDt": "입찰종료일시",
    "usbdNft": "유찰횟수",
    "pbctStatNm": "입찰결과"
}

def fetch_data(pvctTrgtYn):
    """
    특정 수의계약 가능여부(pvctTrgtYn)에 해당하는 데이터를 모든 타겟 지역에 대해 수집합니다.
    """
    all_items = []
    
    for region in TARGET_REGIONS:
        print(f"[{'수의계약' if pvctTrgtYn == 'Y' else '일반진행/예정'}] {region} 데이터 수집 중...")
        page_no = 1
        num_of_rows = 1000  # API 최대 허용치 1000으로 고정
        
        while True:
            params = {
                'serviceKey': SERVICE_KEY,
                'resultType': 'json',
                'numOfRows': num_of_rows,
                'pageNo': page_no,
                'pvctTrgtYn': pvctTrgtYn,
                'prptDivCd': ONBID_CONFIG["prpt_div_cd"],
                'lctnSdnm': region
            }
            
            try:
                response = requests.get(API_URL, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                header = data.get('header', {})
                if header.get('resultCode') != '00':
                    print(f"API Error: {header.get('resultMsg')} (Page: {page_no})")
                    break
                
                body = data.get('body', {})
                items_data = body.get('items', {}).get('item', [])
                
                if isinstance(items_data, dict):
                    # 결과가 1건일 경우 dict로 반환될 수 있음
                    items_data = [items_data]
                
                if not items_data:
                    break
                    
                all_items.extend(items_data)
                print(f"  - {page_no} 페이지 수집 완료 ({len(items_data)} 건)")
                
                # 받아온 아이템 수가 요청한 numOfRows보다 작으면 마지막 페이지이므로 종료
                if len(items_data) < num_of_rows:
                    break
                    
                page_no += 1
                time.sleep(0.5) # API 서버 부하 방지를 위한 딜레이
                
            except Exception as e:
                print(f"Exception 발생: {e}")
                break
                
    return all_items

def process_and_export(regular_items, private_items):
    print("데이터 병합 및 정제 시작...")
    
    # 데이터프레임 변환
    df_regular = pd.DataFrame(regular_items)
    df_private = pd.DataFrame(private_items)
    
    if not df_regular.empty:
        df_regular['pvctTrgtYn_text'] = '일반(진행/예정)'
    if not df_private.empty:
        df_private['pvctTrgtYn_text'] = '수의계약가능'
        
    df_all = pd.concat([df_regular, df_private], ignore_index=True)
    
    if df_all.empty:
        print("수집된 데이터가 없습니다.")
        return
        
    # 중복 제거 (물건관리번호 기준)
    df_all = df_all.drop_duplicates(subset=['cltrMngNo'], keep='last')
    
    # 날짜 포맷 변경 등 후처리 (YYYYMMDDHHMM -> YYYY-MM-DD HH:MM)
    def format_date(x):
        x = str(x)
        if len(x) >= 12 and x.isdigit():
            return f"{x[0:4]}-{x[4:6]}-{x[6:8]} {x[8:10]}:{x[10:12]}"
        return x

    # 관심1.xlsx 양식에 맞추어 컬럼 매핑 (기존 A~T 20개 컬럼 100% 유지 + 우측 참고 컬럼)
    records = []
    for idx, row in df_all.iterrows():
        records.append({
            '번호': '',
            '물건관리번호': row.get('cltrMngNo', ''),
            '공고일자': '', # API에서 제공하지 않는 경우 빈칸
            '등록일자': '', # API에서 제공하지 않는 경우 빈칸
            '입찰시작일시': format_date(row.get('cltrBidBgngDt', '')),
            '입찰마감일시': format_date(row.get('cltrBidEndDt', '')),
            '재산유형': row.get('prptDivNm', ''),
            '회차': row.get('pbctNsq', ''),
            '차수': row.get('pbctsn', ''),
            '공고기관': row.get('orgNm', ''),
            '용도': row.get('cltrUsgSclsCtgrNm') if pd.notna(row.get('cltrUsgSclsCtgrNm')) and row.get('cltrUsgSclsCtgrNm') else row.get('cltrUsgMclsCtgrNm', ''),
            '물건명': row.get('onbidCltrNm', ''),
            '토지면적(㎡)': row.get('landSqms', ''),
            '건물면적(㎡)': row.get('bldSqms', ''),
            '처분방식': row.get('dspsMthodNm', ''),
            '소재지': row.get('cltrRadr', ''),
            '최저입찰가(원)': row.get('lowstBidPrcIndctCont', ''),
            '감정가(원)': row.get('apslEvlAmt', ''),
            '최저입찰가율(%)': row.get('apslPrcCtrsLowstBidRto', ''),
            '물건상태': row.get('pbctStatNm', '') if pd.notna(row.get('pbctStatNm')) and str(row.get('pbctStatNm')).strip() != '' else row.get('pvctTrgtYn_text', ''),
            '공매번호': row.get('pbctNo', ''),
            '취소/회수사유': ''
        })

    active_count = len(records)

    # 과거 매물로 나왔다가 취소·회수된 물건(수의계약 이탈 포함, 낙찰 제외)을 기존 데이터 하단에 추가
    appended_count = 0
    try:
        canceled_records = collect_canceled_and_withdrawn_records(df_all)
        if canceled_records:
            records.extend(canceled_records)
            appended_count = len(canceled_records)
    except Exception as e:
        print(f"[경고] 과거 취소/회수 물건 병합 중 오류 발생 (기존 활성 물건은 정상 저장됩니다): {e}")
        
    df_final = pd.DataFrame(records)
    
    # 금액 콤마 및 숫자 포맷팅
    for col in ["감정가(원)", "최저입찰가(원)"]:
        df_final[col] = pd.to_numeric(df_final[col], errors='coerce').fillna(0)

    # 번호 부여
    df_final['번호'] = range(1, len(df_final) + 1)



    # 엑셀 파일 저장
    time_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"온비드_관심물건_{time_str}.xlsx"
    
    output_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_filename)
    
    with pd.ExcelWriter(output_filepath, engine='openpyxl') as writer:
        df_final.to_excel(writer, index=False, sheet_name='온비드물건목록')
        
        worksheet = writer.sheets['온비드물건목록']
        
        for idx, col in enumerate(df_final.columns):
            try:
                col_max = df_final[col].astype(str).str.len().max()
                col_max = int(col_max) if pd.notna(col_max) else 0
            except Exception:
                col_max = 0
                
            max_len = max(
                col_max if not df_final[col].empty else 0,
                len(str(col))
            ) + 2
            
            try:
                worksheet.column_dimensions[get_column_letter(idx + 1)].width = min(max_len, 50)
            except Exception:
                pass
            
    print(f"엑셀 파일 저장 완료: {output_filepath}")
    print(f"총 {len(df_final)} 개의 물건이 추출되었습니다. (현재 진행/수의계약: {active_count}건 + 과거 취소/회수 추가: {appended_count}건)")
    return output_filepath

def run_crawling():
    print("====== 온비드 공매물건 크롤러 시작 ======")
    # 1. 일반 진행/예정 물건 수집 (pvctTrgtYn='N')
    regular_items = fetch_data('N')
    
    # 2. 수의계약 물건 수집 (pvctTrgtYn='Y')
    private_items = fetch_data('Y')
    
    # 3. 데이터 통합, 정제 및 엑셀 내보내기
    filepath = process_and_export(regular_items, private_items)
    print("====== 온비드 공매물건 크롤러 종료 ======")
    return filepath

if __name__ == "__main__":
    run_crawling()
