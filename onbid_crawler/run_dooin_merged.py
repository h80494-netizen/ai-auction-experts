import subprocess
import os
import sys
import glob
import pandas as pd
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_and_merge():
    print("인천, 서울, 경기 두인경매 크롤러를 차례대로 실행합니다...")
    
    # 1. 스크립트 실행
    scripts = ['incheon_dooin.py', 'seoul_dooin.py', 'kyunggi_dooin.py']
    for script in scripts:
        script_path = os.path.join(BASE_DIR, script)
        if os.path.exists(script_path):
            print(f"{script} 실행 중...")
            subprocess.run([sys.executable, script_path], cwd=BASE_DIR, check=True)
        else:
            print(f"[오류] {script} 파일이 존재하지 않습니다.")

    # 2. 가장 최근에 생성된 엑셀 파일들 찾기 (요약 파일 제외)
    incheon_files = sorted([f for f in glob.glob(os.path.join(BASE_DIR, '인천_두인경매데이터_*.xlsx')) if '요약' not in f], key=os.path.getmtime, reverse=True)
    seoul_files = sorted([f for f in glob.glob(os.path.join(BASE_DIR, '서울_두인경매데이터_*.xlsx')) if '요약' not in f], key=os.path.getmtime, reverse=True)
    kyunggi_files = sorted([f for f in glob.glob(os.path.join(BASE_DIR, '경기도_두인경매데이터_*.xlsx')) if '요약' not in f], key=os.path.getmtime, reverse=True)

    dfs = []
    
    if incheon_files:
        print(f"인천 파일 로드: {incheon_files[0]}")
        dfs.append(pd.read_excel(incheon_files[0]))
    if seoul_files:
        print(f"서울 파일 로드: {seoul_files[0]}")
        dfs.append(pd.read_excel(seoul_files[0]))
    if kyunggi_files:
        print(f"경기 파일 로드: {kyunggi_files[0]}")
        dfs.append(pd.read_excel(kyunggi_files[0]))

    if dfs:
        print("데이터프레임 병합 중...")
        merged_df = pd.concat(dfs, ignore_index=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        merged_filename = f"수도권_두인경매통합_{timestamp}.xlsx"
        merged_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), merged_filename)
        
        # 단일 시트에 저장
        merged_df.to_excel(merged_filepath, index=False, engine='openpyxl')
        print(f"통합 완료: {merged_filepath}")
        return merged_filepath
    else:
        print("병합할 데이터가 없습니다.")
        return None

if __name__ == '__main__':
    run_and_merge()
