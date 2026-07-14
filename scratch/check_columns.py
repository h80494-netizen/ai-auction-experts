import pandas as pd
import requests

input_file = r'c:\Users\llll\Documents\두인경매\바이브코딩\data\경공매데이터_update.xlsx'
df = pd.read_excel(input_file, sheet_name='정리')

print("Columns:", list(df.columns))
print("First row data:")
row = df.iloc[0]
print("경도:", row.get('경도', row.get('x', row.get('X', 'Not found'))))
print("위도:", row.get('위도', row.get('y', row.get('Y', 'Not found'))))
