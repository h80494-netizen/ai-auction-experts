import pandas as pd
df = pd.read_excel('data/경공매데이터_update.xlsx')
if '매각기일' in df.columns:
    print('From 경공매데이터_update.xlsx:')
    print(df['매각기일'].value_counts().head(10))
    print('---')
    
df2 = pd.read_excel('data/경공매데이터_update_대항력.xlsx')
if '매각기일' in df2.columns:
    print('From 경공매데이터_update_대항력.xlsx:')
    print(df2['매각기일'].value_counts().head(10))
    print('---')

import sqlite3
conn = sqlite3.connect('backend/data/map_data.db')
cursor = conn.cursor()
cursor.execute("SELECT sale_date, COUNT(*) FROM auctions GROUP BY sale_date ORDER BY COUNT(*) DESC LIMIT 10")
print('From DB:')
for row in cursor.fetchall():
    print(row)
conn.close()
