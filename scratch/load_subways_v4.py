import sqlite3
import pandas as pd
import sys
import os
import json
import numpy as np

DB_PATH = 'backend/data/map_data.db'
EXCEL_PATH = 'data/지하철역1(위례과천선포함).xlsx'

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dLat = np.radians(lat2 - lat1)
    dLon = np.radians(lon2 - lon1)
    a = np.sin(dLat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dLon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return R * c

def sort_stations_nearest_neighbor(stations):
    if not stations: return []
    start_idx = min(range(len(stations)), key=lambda i: stations[i]['lng'])
    unvisited = stations[:]
    current = unvisited.pop(start_idx)
    sorted_path = [current]
    while unvisited:
        nearest_idx = min(range(len(unvisited)), 
                          key=lambda i: haversine(current['lat'], current['lng'], 
                                                  unvisited[i]['lat'], unvisited[i]['lng']))
        current = unvisited.pop(nearest_idx)
        sorted_path.append(current)
    return sorted_path

def main():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("DROP TABLE IF EXISTS subways")
        cursor.execute("CREATE TABLE subways (id INTEGER PRIMARY KEY, line TEXT, name TEXT, address TEXT, lat REAL, lng REAL, status TEXT)")

        df = pd.read_excel(EXCEL_PATH, sheet_name=0, header=1)
        # Columns: 구/시군, 노선명, 지하철(역), 도로명주소 (지번주소 등), 위도, 경도, 운영현황 및 기타
        
        inserted = 0
        for _, row in df.iterrows():
            line = str(row.iloc[1]).strip()
            name = str(row.iloc[2]).strip()
            address = str(row.iloc[3]).strip()
            try:
                lat = float(row.iloc[4])
                lng = float(row.iloc[5])
            except:
                lat, lng = 0.0, 0.0
            status = str(row.iloc[6]).strip() if not pd.isna(row.iloc[6]) else ""

            if line == 'nan' or name == 'nan':
                continue
                
            if lat == 0.0 or lng == 0.0:
                continue

            cursor.execute("INSERT INTO subways (line, name, address, lat, lng, status) VALUES (?, ?, ?, ?, ?, ?)",
                (line, name, address, lat, lng, status)
            )
            inserted += 1

        print(f"Subways loaded successfully: {inserted} records")

        # Now recreate subway_lines
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subway_lines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                line TEXT,
                coordinates_json TEXT,
                status TEXT
            )
        ''')
        cursor.execute('DELETE FROM subway_lines')
        
        # Read stations
        cursor.execute('SELECT id, line, name, lat, lng, status FROM subways WHERE lat IS NOT NULL AND lng IS NOT NULL')
        rows = cursor.fetchall()
        
        lines_dict = {}
        for r in rows:
            line_name = str(r[1]).strip()
            status = str(r[5]).strip()
            if not line_name:
                continue
            key = (line_name, status)
            if key not in lines_dict:
                lines_dict[key] = []
            lines_dict[key].append({'id': r[0], 'name': r[2], 'lat': r[3], 'lng': r[4]})
            
        lines_inserted = 0
        for (line_name, status), stations in lines_dict.items():
            if len(stations) < 2:
                continue
            
            sorted_stations = sort_stations_nearest_neighbor(stations)
            coords = [[s['lat'], s['lng']] for s in sorted_stations]
            
            cursor.execute('INSERT INTO subway_lines (line, coordinates_json, status) VALUES (?, ?, ?)',
                           (line_name, json.dumps(coords), status))
            lines_inserted += 1
            
        print(f"Successfully processed and stored {lines_inserted} subway lines.")

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
