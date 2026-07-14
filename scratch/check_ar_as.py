import pandas as pd
import requests

input_file = r'c:\Users\llll\Documents\두인경매\바이브코딩\data\경공매데이터_update.xlsx'
df = pd.read_excel(input_file, sheet_name='정리')

print("Column at AR (index 43):", df.columns[43])
print("Column at AS (index 44):", df.columns[44])

# Let's check the first few rows of these columns
print("First 5 rows for AR, AS:")
print(df.iloc[:5, 43:45])
