import pandas as pd
import os
import sys

# Force output to use utf-8
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

print("=== apt_information.xlsx L15/O Column check ===")
apt_path = 'data/apt_information.xlsx'
if os.path.exists(apt_path):
    df_apt = pd.read_excel(apt_path, header=1, nrows=2)
    cols = list(df_apt.columns)
    print("Header L1 columns:")
    for idx, c in enumerate(cols):
        print(f"Index {idx} (Excel col {idx+1}): {c}")
        
    if len(cols) >= 15:
        print(f"\n15th Column (O Col, index 14) name is: '{cols[14]}'")
        # Also print first row
        print("First row data:")
        print(df_apt.iloc[0].to_dict())

print("\n=== 서울시 대로변 횡단보도 위치정보.csv cp949 check ===")
cross_path = 'data/서울시 대로변 횡단보도 위치정보.csv'
if os.path.exists(cross_path):
    df_cross = pd.read_csv(cross_path, encoding='cp949', nrows=2)
    print("Columns:")
    print(list(df_cross.columns))
    print("First row:")
    print(df_cross.iloc[0].to_dict())

print("\n=== 서울시 자치구별 도보 네트워크 공간정보.csv cp949 check ===")
walk_net_path = 'data/서울시 자치구별 도보 네트워크 공간정보.csv'
if os.path.exists(walk_net_path):
    df_walk = pd.read_csv(walk_net_path, encoding='cp949', nrows=2)
    print("Columns:")
    print(list(df_walk.columns))
    print("First row:")
    print(df_walk.iloc[0].to_dict())
