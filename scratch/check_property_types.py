import sqlite3
import os
import sys

# Set standard output encoding to utf-8
if sys.stdout.encoding != 'utf-8':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Checking property types in realprice_grids:")
cursor.execute("SELECT property_type, COUNT(*) FROM realprice_grids GROUP BY property_type")
for row in cursor.fetchall():
    # Print the raw bytes representation if there's any encoding mismatch
    name = row[0]
    # Check if name is str or bytes
    if isinstance(name, str):
        # try to encode/decode if it was mis-decoded
        try:
            name_bytes = name.encode('cp949')
            name_decoded = name_bytes.decode('utf-8')
            print(f" - {name_decoded} (re-decoded): {row[1]}")
        except Exception:
            try:
                name_bytes = name.encode('utf-8')
                print(f" - {name} (as is): {row[1]} (bytes: {name_bytes.hex()})")
            except Exception:
                print(f" - {name} (raw): {row[1]}")
    else:
        print(f" - {name} (non-string): {row[1]}")

conn.close()
