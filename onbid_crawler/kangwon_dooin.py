import requests
import json
import pandas as pd
from datetime import datetime
import time
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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
        # 메인 페이지 접속
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

def get_auction_data(page_no):
    """특정 페이지의 경매 데이터를 가져오는 함수"""
    global cookies  # 함수 시작 부분에 global 선언
    
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
        'siCd': '51',
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
    
    # 디버깅: 첫 번째 요청일 때만 URL 출력
    if page_no == 1:
        print(f"[DEBUG] 요청 URL: {url}")
        print(f"[DEBUG] 파라미터 개수: {len(params)}")
        print(f"[DEBUG] 사용 중인 쿠키: {cookies}")
    
    # GET 요청
    response = session.get(url, params=params, cookies=cookies, headers=headers, timeout=10)
    
    # 404 에러 발생 시 세션 재획득 후 재시도
    if response.status_code == 404 and page_no == 1:
        print("[WARN] 404 에러 발생, 세션 재획득 시도...")
        cookies = get_session_cookies()
        response = session.get(url, params=params, cookies=cookies, headers=headers, timeout=10)
    
    return response

def main():
    all_data = []
    page_no = 1
    total_count = 0
    
    print("강원도 두인경매 데이터 크롤링을 시작합니다...")
    
    while True:
        try:
            print(f"\n{page_no}페이지 크롤링 중...")
            
            # API 호출
            response = get_auction_data(page_no)
            
            # 응답 확인
            if response.status_code != 200:
                print(f"API 호출 실패: 상태 코드 {response.status_code}")
                print(f"요청 URL: {response.url}")
                print(f"응답 내용: {response.text[:1000]}")
                print("\n[해결 방법]")
                print("1. 브라우저에서 https://www.dooinauction.com 접속")
                print("2. F12 개발자 도구 열기 -> Network 탭")
                print("3. 경매 목록 페이지에서 실제 API 요청 확인")
                print("4. 요청 헤더에서 새로운 PHPSESSID 쿠키 복사")
                print("5. 코드의 cookies 딕셔너리에 업데이트")
                break
            
            # JSON 파싱
            try:
                response_json = response.json()
            except json.JSONDecodeError as e:
                print(f"JSON 파싱 실패: {e}")
                print("원본 응답:")
                print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
                break
            
            # 데이터 추출
            current_data = []
            
            # 두인경매 API 응답 구조 처리
            if 'item' in response_json:
                current_data = response_json['item']
                total_available = response_json.get('totalCnt', 0)
                print(f"전체 데이터 개수: {total_available}개")
            
            current_count = len(current_data)
            print(f"현재 페이지 데이터 개수: {current_count}개")
            
            # 데이터가 20개 미만이면 크롤링 중단
            if current_count < 20:
                print(f"데이터가 {current_count}개로 20개 미만입니다. 크롤링을 중단합니다.")
                all_data.extend(current_data)
                total_count += current_count
                break
            
            # 데이터 추가
            all_data.extend(current_data)
            total_count += current_count
            
            print(f"현재까지 수집된 데이터: {total_count}개")
            
            # 다음 페이지로
            page_no += 1
            
            # 서버 부하 방지를 위한 랜덤 딜레이 (최대 10초)
            sleep_time = random.uniform(1, 10)
            print(f"{sleep_time:.2f}초 대기 중...")
            time.sleep(sleep_time)
                
        except Exception as e:
            print(f"오류 발생: {e}")
            break
    
    # 결과 출력
    print(f"\n=== 크롤링 완료 ===")
    print(f"총 수집된 데이터: {total_count}개")
    print(f"크롤링한 페이지 수: {page_no}페이지")
    
    # 엑셀로 저장
    if all_data:
        try:
            # 데이터프레임 생성
            df = pd.DataFrame(all_data)
            
            # 파일명 생성 (현재 시간 포함)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"강원도_두인경매데이터_{timestamp}.xlsx"
            
            # 엑셀로 저장
            df.to_excel(filename, index=False, engine='openpyxl')
            print(f"데이터가 {filename}에 저장되었습니다.")
            
            # 주요 컬럼만 선택해서 간단한 요약 파일도 생성
            if len(df.columns) > 0:
                # 주요 컬럼들 선택
                summary_columns = ['tid', 'ctgr', 'saNo', 'crtDpt', 'regnAdrs', 'apslAmt', 'minbAmt', 'bidDt', 'statNm']
                available_columns = [col for col in summary_columns if col in df.columns]
                
                if available_columns:
                    summary_df = df[available_columns]
                    summary_filename = f"강원도_두인경매데이터_요약_{timestamp}.xlsx"
                    summary_df.to_excel(summary_filename, index=False, engine='openpyxl')
                    print(f"요약 데이터가 {summary_filename}에 저장되었습니다.")
                else:
                    # 처음 10개 컬럼을 요약으로 사용
                    summary_columns = df.columns[:10].tolist()
                    summary_df = df[summary_columns]
                    summary_filename = f"강원도_두인경매데이터_요약_{timestamp}.xlsx"
                    summary_df.to_excel(summary_filename, index=False, engine='openpyxl')
                    print(f"요약 데이터가 {summary_filename}에 저장되었습니다.")
            
        except Exception as e:
            print(f"엑셀 저장 중 오류 발생: {e}")
    else:
        print("저장할 데이터가 없습니다.")

if __name__ == "__main__":
    main()
    
