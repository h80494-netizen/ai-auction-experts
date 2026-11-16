import requests
import json
import pandas as pd
from datetime import datetime
import time
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os

# 세션 생성 및 재시도 설정
session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

def get_session_cookies():
    """두인경매 사이트에 접속하여 유효한 세션 쿠키 획득"""
    try:
        main_url = 'https://www.dooinauction.com/ca/caList.php?srchHistory=16'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        resp = session.get(main_url, headers=headers, timeout=10)
        cookies = session.cookies.get_dict()
        print(f"[INFO] 세션 쿠키 획득: {cookies}")
        return cookies
    except Exception as e:
        print(f"[WARN] 세션 쿠키 획득 실패: {e}")
        return {'PHPSESSID': '15fbf4849ecd7ff4bd2678c3c6bd0475', 'TKC_ABUSER': '0'}

# 초기 쿠키 설정
cookies = get_session_cookies()

headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Referer': 'https://www.dooinauction.com/ca/caList.php?srchHistory=16',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

def get_auction_data(page_no, siCd):
    """특정 페이지의 경매 데이터를 가져오는 함수"""
    global cookies
    
    params = {
        'dataSize': '20',
        'pageNo': str(page_no),
        'ck_photo': '0',
        'lsType': '0',
        'odrCol': '14',
        'odrAds': '0',
        'srchFR': '0',
        'idxFR': '0',
        'stat': '11',
        'srchCase': 'srchAll',
        'siCd': siCd,
        'guCd': '0',
        'dnCd': '0',
        'sptArr[0][]': ['0', '0'],
        'ctgr': '',
        'chkCtgrsCd[]': [
            '201013', '201014', '201015,201017,201021', '201020', '201010',
            '201011,201012', '201022', '201016', '201018', '201110,201120,201124',
            '201111,201019', '201130', '201122', '201123', '201131', '201121',
            '201118', '201112', '201113', '201116', '201117', '201128',
            '201132,201115,201119,201125,201126,201127,201129,201310,201311,201312,201114',
            '201210', '201216', '201211', '201212', '201213', '201214', '201215',
            '101010', '101011', '101012', '101014', '101017', '101037', '101023',
            '101020', '101031', '101033', '101035', '101036', '101013', '101018',
            '101019', '101021', '101022', '101024', '101030', '101032', '101034',
            '101025', '101026', '101027', '101015', '101016', '101028', '101029',
        ],
        'chkAllCtgr': '0',
        'fbCntBgn': '0',
        'fbCntEnd': '0',
        'apslAmtBgn': '0',
        'apslAmtEnd': '0',
        'minbAmtBgn': '0',
        'minbAmtEnd': '0',
        'totFlrBgn': '0',
        'totFlrEnd': '0',
        'flrBgn': '0',
        'flrEnd': '0',
        'baseFlr': '0',
        'dpslDvsn': '0',
        'local': '0',
        'line': '0',
        'station': '0',
        'distance': '0',
        'adrsEtcType': '0',
        'adrsEtc': '',
        'sn1': '0',
        'sn2': '0',
        'pn': '0',
        'bgnDt': '',
        'endDt': '',
        'landSqmBgn': '0',
        'landSqmEnd': '0',
        'bldgSqmBgn': '0',
        'bldgSqmEnd': '0',
        'prsvBgn': '0',
        'prsvEnd': '0',
        'preBgnDt': '',
        'preEndDt': '',
        'auctType': '0',
        'splSrchType': '0',
    }

    url = 'https://www.dooinauction.com/ca/res/AuctList.php'
    
    response = session.get(url, params=params, cookies=cookies, headers=headers, timeout=10)
    
    if response.status_code == 404 and page_no == 1:
        print("[WARN] 404 에러 발생, 세션 재획득 시도...")
        cookies = get_session_cookies()
        response = session.get(url, params=params, cookies=cookies, headers=headers, timeout=10)
    
    return response

def crawl_region(region_name, si_cd):
    """특정 지역의 데이터를 크롤링"""
    all_data = []
    page_no = 1
    total_count = 0
    
    print(f"\n[{region_name}] 두인경매 데이터 크롤링을 시작합니다...")
    
    while True:
        try:
            print(f"  - {region_name} {page_no}페이지 크롤링 중...")
            
            response = get_auction_data(page_no, si_cd)
            
            if response.status_code != 200:
                print(f"  [오류] API 호출 실패: 상태 코드 {response.status_code}")
                break
            
            try:
                response_json = response.json()
            except json.JSONDecodeError as e:
                print(f"  [오류] JSON 파싱 실패: {e}")
                break
            
            current_data = []
            if 'item' in response_json:
                current_data = response_json['item']
            
            current_count = len(current_data)
            
            if current_count < 20:
                all_data.extend(current_data)
                total_count += current_count
                break
            
            all_data.extend(current_data)
            total_count += current_count
            
            sleep_time = random.uniform(1, 10)
            print(f"  - {sleep_time:.2f}초 대기 중...")
            time.sleep(sleep_time) # 부하 방지
                
        except Exception as e:
            print(f"  [오류] 발생: {e}")
            break
            
    print(f"[{region_name}] 크롤링 완료 (총 {total_count}개 수집)")
    return all_data

def main():
    regions = [
        {'name': '서울', 'siCd': '11', 'sheet_name': '서울'},
        {'name': '경기', 'siCd': '41', 'sheet_name': '경기'},
        {'name': '인천', 'siCd': '28', 'sheet_name': '인천'}
    ]
    
    region_dataframes = {}
    total_data_collected = 0
    
    print("====== 두인경매 수도권(서울/경기/인천) 크롤러 시작 ======")
    for region in regions:
        data = crawl_region(region['name'], region['siCd'])
        if data:
            region_dataframes[region['sheet_name']] = pd.DataFrame(data)
            total_data_collected += len(data)
        else:
            region_dataframes[region['sheet_name']] = pd.DataFrame()
            
    print(f"\n전체 크롤링 완료. 총 수집된 데이터: {total_data_collected}개")
    
    if total_data_collected > 0:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"수도권_두인경매통합_{timestamp}.xlsx"
            filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
            
            print(f"\n엑셀 파일 생성 중: {filename} ...")
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                for sheet_name, df in region_dataframes.items():
                    if not df.empty:
                        df.to_excel(writer, index=False, sheet_name=sheet_name)
                        
                        # 열 너비 자동 조정
                        worksheet = writer.sheets[sheet_name]
                        for idx, col in enumerate(df.columns):
                            max_len = max(
                                df[col].astype(str).map(len).max() if not df[col].empty else 0,
                                len(col)
                            ) + 2
                            worksheet.column_dimensions[chr(65 + idx % 26)].width = min(max_len, 50)
                            
            print(f"저장 완료: {filepath}")
            
        except Exception as e:
            print(f"엑셀 저장 중 오류 발생: {e}")
    else:
        print("저장할 데이터가 없습니다.")

if __name__ == "__main__":
    main()
