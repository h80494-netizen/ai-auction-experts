import sqlite3
import pandas as pd

excel_path = 'data/경공매데이터_update_대항력.xlsx'
db_path = 'backend/data/map_data.db'

print("Loading Excel...")
try:
    df = pd.read_excel(excel_path)
except Exception as e:
    print(f"Failed to load {excel_path}, trying original file: {e}")
    df = pd.read_excel('data/경공매데이터_update.xlsx')

print("Excel loaded. Finding case numbers and dates...")

date_map = {}
for idx, row in df.iterrows():
    case_no = str(row.get('사건번호', '')).strip()
    date_val = str(row.get('입찰일', '')).strip()
    if case_no and date_val and date_val != 'nan':
        date_map[case_no] = date_val[:10]

print(f"Found {len(date_map)} unique case numbers with dates.")

print("Updating DB...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

updated = 0
for case_no, sale_date in date_map.items():
    cursor.execute("UPDATE auctions SET sale_date = ? WHERE case_no = ?", (sale_date, case_no))
    updated += cursor.rowcount

conn.commit()
print(f"Updated {updated} rows in DB.")

# Verify
cursor.execute("SELECT sale_date, COUNT(*) FROM auctions GROUP BY sale_date ORDER BY COUNT(*) DESC LIMIT 10")
print("Top 10 dates in DB after update:")
for r in cursor.fetchall():
    print(r)

conn.close()
