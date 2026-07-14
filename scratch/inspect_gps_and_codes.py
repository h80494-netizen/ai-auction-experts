import pandas as pd
import os
import sys

if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

print("=== GPS주소와 거리찾기_260504.xlsx check ===")
gps_path = 'data/GPS주소와 거리찾기_260504.xlsx'
if os.path.exists(gps_path):
    df_gps = pd.read_excel(gps_path, nrows=5)
    print("Columns:")
    print(list(df_gps.columns))
    print("First row:")
    print(df_gps.iloc[0].to_dict())

print("\n=== 도보네트워크_링크노드유형코드.xlsx check ===")
code_path = 'data/도보네트워크_링크노드유형코드.xlsx'
if os.path.exists(code_path):
    # let's inspect all sheets
    xl = pd.ExcelFile(code_path)
    print("Sheet names:", xl.sheet_names)
    for sh in xl.sheet_names:
        print(f"\n--- Sheet: {sh} ---")
        df_sh = xl.parse(sh, nrows=10)
        print(df_sh.to_string())
