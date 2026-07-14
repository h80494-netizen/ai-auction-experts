import sqlite3
import sys

if sys.stdout.encoding != 'utf-8':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

conn = sqlite3.connect('backend/data/map_data.db')
cursor = conn.cursor()

cursor.execute("SELECT property_type, COUNT(DISTINCT (lat || ',' || lng)) as unique_coords, COUNT(*) FROM realprice_grids GROUP BY property_type")
print("Distinct coordinate count vs total row count:")
for row in cursor.fetchall():
    print(f" - {row[0]}: {row[1]} unique coordinates out of {row[2]} rows")

print("\nSample coordinates for each type:")
for ptype in ['아파트', '다세대', '오피스텔', '단독', '토지', '상업업무용', '공장창고등', '분양권']:
    cursor.execute("SELECT lat, lng, avg_price_per_pyeong FROM realprice_grids WHERE property_type=? LIMIT 5", (ptype,))
    rows = cursor.fetchall()
    print(f" - {ptype}: {rows}")

conn.close()
