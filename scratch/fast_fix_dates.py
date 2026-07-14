import sqlite3
import re

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all sale_dates
cursor.execute("SELECT id, sale_date FROM auctions WHERE sale_date IS NOT NULL AND sale_date != ''")
rows = cursor.fetchall()

updated = 0
for row_id, sale_date in rows:
    # sale_date is something like '2016-07-26'
    # we want to swap the '16' (DD) with '26' (YY)
    m = re.match(r'^20(\d{2})-(\d{2})-(\d{2})(.*)$', sale_date)
    if m:
        xx = m.group(1) # actually the day
        mm = m.group(2) # month
        yy = m.group(3) # actually the year (26)
        rest = m.group(4) # time if any
        
        # New date: 20yy-mm-xx
        correct_date = f"20{yy}-{mm}-{xx}{rest}"
        
        cursor.execute("UPDATE auctions SET sale_date = ? WHERE id = ?", (correct_date, row_id))
        updated += 1

conn.commit()
print(f"Updated {updated} sale dates.")

cursor.execute("SELECT sale_date, COUNT(*) FROM auctions GROUP BY sale_date ORDER BY COUNT(*) DESC LIMIT 10")
for r in cursor.fetchall():
    print(r)

conn.close()
