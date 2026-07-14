import sqlite3
import pandas as pd

conn = sqlite3.connect('backend/data/map_data.db')
cursor = conn.cursor()
cursor.execute("SELECT case_no, sale_date FROM auctions WHERE sale_date LIKE '2016-07-26%' LIMIT 10")
print('From DB for 2016-07-26:')
for row in cursor.fetchall():
    print(row)
conn.close()

# Also quickly check if the Excel has the same dates using a safer python approach
import csv
print('Checking raw text in Excel using pandas with minimal processing...')
df = pd.read_excel('data/경공매데이터_update_대항력.xlsx', nrows=50)
if '사건번호' in df.columns and '매각기일' in df.columns:
    print('Sample from Excel:')
    print(df[['사건번호', '매각기일']].head())
