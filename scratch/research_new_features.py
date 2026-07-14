import pandas as pd
import sqlite3

# Inspect 아파트단지정보.xlsx
df = pd.read_excel('c:/Users/llll/Documents/두인경매/바이브코딩/data/아파트단지정보.xlsx', nrows=5)
print("=== 아파트단지정보.xlsx Columns ===")
print(df.columns.tolist())
print("\nFirst 2 rows:")
print(df.head(2).to_dict('records'))

# Inspect database tables for parcel data
conn = sqlite3.connect('c:/Users/llll/Documents/두인경매/바이브코딩/backend/data/map_data.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("\n=== DB Tables ===")
print([r[0] for r in cursor.fetchall()])
conn.close()

# Also check backend endpoints related to road or heatmap
print("\n=== Searching for road / heatmap in backend ===")
import os
app_py_path = 'c:/Users/llll/Documents/두인경매/바이브코딩/backend/app.py'
if os.path.exists(app_py_path):
    with open(app_py_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if '도로' in line or 'road' in line.lower() or 'heat' in line.lower() or '인구' in line:
                print(f"Line {i}: {line.strip()}")
