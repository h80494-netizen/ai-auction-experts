import subprocess
import os
import sys
import glob
import pandas as pd
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_and_merge():
    print("강원도, 충청남도, 전라남도(광주 포함) 두인경매 크롤러를 차례대로 실행합니다...")
    
    # 1. 스크립트 실행
    scripts = ['kangwon_dooin.py', 'chungnam_dooin.py', 'jeonnam_dooin.py']
    for script in scripts:
        script_path = os.path.join(BASE_DIR, script)
        if os.path.exists(script_path):
            print(f"\n>>> {script} 실행 중...")
            subprocess.run([sys.executable, script_path], cwd=BASE_DIR, check=True)
        else:
            print(f"[오류] {script} 파일이 존재하지 않습니다.")

    # 2. 가장 최근에 생성된 엑셀 파일들 찾기 (요약 파일 제외)
    kangwon_files = sorted([f for f in glob.glob(os.path.join(BASE_DIR, '강원도_두인경매데이터_*.xlsx')) if '요약' not in f], key=os.path.getmtime, reverse=True)
    chungnam_files = sorted([f for f in glob.glob(os.path.join(BASE_DIR, '충청남도_두인경매데이터_*.xlsx')) if '요약' not in f], key=os.path.getmtime, reverse=True)
    jeonnam_files = sorted([f for f in glob.glob(os.path.join(BASE_DIR, '전라남도_두인경매데이터_*.xlsx')) if '요약' not in f], key=os.path.getmtime, reverse=True)

    dfs = []
    
    if kangwon_files:
        print(f"강원 파일 로드: {kangwon_files[0]}")
        dfs.append(pd.read_excel(kangwon_files[0]))
    if chungnam_files:
        print(f"충남 파일 로드: {chungnam_files[0]}")
        dfs.append(pd.read_excel(chungnam_files[0]))
    if jeonnam_files:
        print(f"전남/광주 파일 로드: {jeonnam_files[0]}")
        dfs.append(pd.read_excel(jeonnam_files[0]))

    if dfs:
        print("\n데이터프레임 병합 중...")
        merged_df = pd.concat(dfs, ignore_index=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        merged_filename = f"지방권_두인경매통합_{timestamp}.xlsx"
        merged_filepath = os.path.join(BASE_DIR, merged_filename)
        
        # 단일 시트에 저장
        merged_df.to_excel(merged_filepath, index=False, engine='openpyxl')
        print(f"통합 완료: {merged_filepath}")
        return merged_filepath
    else:
        print("병합할 데이터가 없습니다.")
        return None

if __name__ == '__main__':
    run_and_merge()
