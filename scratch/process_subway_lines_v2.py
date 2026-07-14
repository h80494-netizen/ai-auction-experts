import sqlite3
import os
import json
import numpy as np
import sys

# Force output to use utf-8
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

DB_PATH = 'backend/data/map_data.db'

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in kilometers
    dLat = np.radians(lat2 - lat1)
    dLon = np.radians(lon2 - lon1)
    a = np.sin(dLat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dLon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return R * c

def sort_stations_nearest_neighbor(stations):
    if not stations:
        return []
    
    # Heuristic: start with endpoint (min longitude)
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

def process_subway_lines_v2():
    print("Connecting to map_data.db...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if table subway_lines exists, drop and recreate with status column
    cursor.execute("DROP TABLE IF EXISTS subway_lines")
    cursor.execute('''
        CREATE TABLE subway_lines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            line TEXT,
            status TEXT,
            coordinates_json TEXT
        )
    ''')
    
    # Read all stations
    cursor.execute('SELECT id, line, name, lat, lng, status FROM subways WHERE lat IS NOT NULL AND lng IS NOT NULL')
    rows = cursor.fetchall()
    
    lines_dict = {}
    for r in rows:
        line_name = str(r[1]).strip()
        if not line_name:
            continue
        if line_name not in lines_dict:
            lines_dict[line_name] = []
        lines_dict[line_name].append({
            'id': r[0],
            'name': r[2],
            'lat': r[3],
            'lng': r[4],
            'status': str(r[5]).strip()
        })
        
    print(f"Found {len(lines_dict)} unique lines in subways table.")
    
    inserted = 0
    for line_name, stations in lines_dict.items():
        if len(stations) < 2:
            # If a line has only 1 station, we cannot draw a line
            continue
            
        # Sort stations using nearest neighbor
        sorted_stations = sort_stations_nearest_neighbor(stations)
        
        # Split into contiguous segments of same status
        # If both adjacent stations are '기존', segment is '기존'.
        # Else, segment is '예정' (planned/new/extended).
        sub_lines = []
        current_status = None
        current_coords = []
        
        for i in range(len(sorted_stations) - 1):
            s1 = sorted_stations[i]
            s2 = sorted_stations[i+1]
            
            # Segment status
            if s1['status'] == '기존' and s2['status'] == '기존':
                status = '기존'
            else:
                status = '예정'
                
            if current_status is None:
                current_status = status
                current_coords = [[s1['lat'], s1['lng']], [s2['lat'], s2['lng']]]
            elif current_status == status:
                current_coords.append([s2['lat'], s2['lng']])
            else:
                # Save previous sub-line
                sub_lines.append({
                    'status': current_status,
                    'coords': current_coords
                })
                # Start new sub-line
                current_status = status
                current_coords = [[s1['lat'], s1['lng']], [s2['lat'], s2['lng']]]
                
        if current_coords:
            sub_lines.append({
                'status': current_status,
                'coords': current_coords
            })
            
        # Insert grouped segments into database
        for sl in sub_lines:
            cursor.execute('INSERT INTO subway_lines (line, status, coordinates_json) VALUES (?, ?, ?)',
                           (line_name, sl['status'], json.dumps(sl['coords'])))
            inserted += 1
            
    conn.commit()
    conn.close()
    print(f"Successfully processed and stored {inserted} subway line segments (solid/dashed splits).")

if __name__ == '__main__':
    process_subway_lines_v2()
