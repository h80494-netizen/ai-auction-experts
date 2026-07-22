import pandas as pd
import sqlite3
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

def sort_stations(stations):
    if not stations: return []
    start_idx = min(range(len(stations)), key=lambda i: stations[i]['lng'])
    unvisited = stations[:]
    current = unvisited.pop(start_idx)
    sorted_path = [current]
    while unvisited:
        nearest_idx = min(range(len(unvisited)), key=lambda i: haversine(current['lat'], current['lng'], unvisited[i]['lat'], unvisited[i]['lng']))
        current = unvisited.pop(nearest_idx)
        sorted_path.append(current)
    return sorted_path

def add_seobu():
    df = pd.read_excel(EXCEL_PATH, header=1)
    # The header is at index 1 (row 2 in excel). 
    # Columns: 0: 구/분, 1: 호선명, 2: 전철역, 3: 주소, 4: 위도, 5: 경도, 6: 운영현황
    
    # Filter for 서부경전철
    seobu = df[df.iloc[:, 1].astype(str).str.contains('서부', na=False)].copy()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Clean old seobu if any
    cursor.execute("DELETE FROM subways WHERE line LIKE '%서부%'")
    cursor.execute("DELETE FROM subway_lines WHERE line LIKE '%서부%'")
    
    print(f"Found {len(seobu)} stations for 서부경전철")
    
    stations = []
    for idx, row in seobu.iterrows():
        line = str(row.iloc[1]).strip()
        name = str(row.iloc[2]).strip()
        address = str(row.iloc[3]).strip()
        lat = row.iloc[4]
        lng = row.iloc[5]
        status = str(row.iloc[6]).strip()
        
        # Insert into subways table
        cursor.execute('''
            INSERT INTO subways (line, name, address, lat, lng, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (line, name, address, lat, lng, status))
        
        stations.append({'lat': lat, 'lng': lng, 'name': name})
        
    # Now build the line
    sorted_stations = sort_stations(stations)
    coords = [[s['lat'], s['lng']] for s in sorted_stations]
    
    cursor.execute('INSERT INTO subway_lines (line, coordinates_json) VALUES (?, ?)',
                   ('서부경전철', json.dumps(coords)))
                   
    conn.commit()
    conn.close()
    print("Seobu line added successfully.")

if __name__ == '__main__':
    add_seobu()
