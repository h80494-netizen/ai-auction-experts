import pandas as pd
import sqlite3
import os
import sys

# Force output to use utf-8
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

excel_path = "data/지하철역사.xlsx"
db_path = "backend/data/map_data.db"

if not os.path.exists(excel_path):
    print(f"Error: {excel_path} not found")
    sys.exit(1)
if not os.path.exists(db_path):
    print(f"Error: {db_path} not found")
    sys.exit(1)

# Load excel sheet
df = pd.read_excel(excel_path, sheet_name="예정역포함")

# Clean column names (strip spaces)
df.columns = [c.strip() for c in df.columns]
print("Cleaned Excel Columns:", df.columns.tolist())

# Connect to DB
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check current columns of subways table
cursor.execute("PRAGMA table_info(subways)")
cols = [c[1] for c in cursor.fetchall()]
print("DB subways Columns:", cols)

# Update query helper
# We can match by line, name, and address, or lat/lng.
# Let's match by lat/lng or address or line+name.
# Let's write a robust matching logic.
matched_count = 0
unmatched_count = 0

for idx, row in df.iterrows():
    line = str(row['노선']).strip()
    name = str(row['지하철명']).strip()
    address = str(row['지번주소']).strip()
    lat = float(row['위도'])
    lng = float(row['경도'])
    status = str(row['상황']).strip()
    
    # Try exact match by lat, lng
    cursor.execute("SELECT id, status FROM subways WHERE ABS(lat - ?) < 0.00001 AND ABS(lng - ?) < 0.00001", (lat, lng))
    db_row = cursor.fetchone()
    
    if db_row:
        db_id, db_status = db_row
        cursor.execute("UPDATE subways SET status = ? WHERE id = ?", (status, db_id))
        matched_count += 1
    else:
        # Try match by line and name
        cursor.execute("SELECT id, status FROM subways WHERE line = ? AND name = ?", (line, name))
        db_rows = cursor.fetchall()
        if len(db_rows) == 1:
            db_id, db_status = db_rows[0]
            cursor.execute("UPDATE subways SET status = ? WHERE id = ?", (status, db_id))
            matched_count += 1
        elif len(db_rows) > 1:
            # Match by address similarity or pick the first
            db_id = db_rows[0][0]
            cursor.execute("UPDATE subways SET status = ? WHERE id = ?", (status, db_id))
            matched_count += 1
        else:
            # No match found, print warning or insert if missing?
            # Actually, let's check how many are unmatched first.
            unmatched_count += 1

conn.commit()
print(f"Updated {matched_count} rows in subways table.")
print(f"Unmatched rows from Excel: {unmatched_count}")

# Print status distribution in DB now
cursor.execute("SELECT status, COUNT(*) FROM subways GROUP BY status")
db_stats = cursor.fetchall()
print("\nUpdated DB subways status distribution:")
for ds in db_stats:
    print(ds)

conn.close()
