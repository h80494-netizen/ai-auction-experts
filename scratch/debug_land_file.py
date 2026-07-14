import pandas as pd
import sys

FILE_PATH = r"c:\Users\llll\Documents\두인경매\바이브코딩\realprice\MOLIT_인천광역시_토지_매매_1780926628.csv"

# Try reading with utf-8 first
try:
    df = pd.read_csv(FILE_PATH, skiprows=15, encoding='utf-8', nrows=2)
    print("UTF-8 read columns:", [c.encode('ascii', 'backslashreplace').decode('ascii') for c in df.columns])
except Exception as e:
    print("UTF-8 read failed:", e)

# Try reading with cp949
try:
    df = pd.read_csv(FILE_PATH, skiprows=15, encoding='cp949', nrows=2)
    print("CP949 read columns:", [c.encode('ascii', 'backslashreplace').decode('ascii') for c in df.columns])
except Exception as e:
    print("CP949 read failed:", e)
