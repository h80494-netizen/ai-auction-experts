import sqlite3
import pandas as pd
import glob
import os

print("--- Database Schema ---")
conn = sqlite3.connect('data/map_data.db')
cur = conn.cursor()
cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
for row in cur.fetchall():
    if 'population' in row[0] or 'commercial' in row[0]:
        print(f"Table: {row[0]}")
        print(row[1])
        print()

print("--- CSV Previews ---")
files = glob.glob('data/500격자주거직장인구/*.csv')
for f in files:
    print(f"\nFile: {os.path.basename(f)}")
    df = pd.read_csv(f, encoding='cp949', nrows=3)
    print(df.head())
