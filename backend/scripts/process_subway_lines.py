import sqlite3
import os
import json
import numpy as np

DB_PATH = os.path.join(os.path.dirname(__file__), '../data/map_data.db')

def haversine(lat1, lon1, lat2, lon2):
    # Calculate great-circle distance between two points on Earth
    R = 6371.0  # Earth radius in kilometers
    dLat = np.radians(lat2 - lat1)
    dLon = np.radians(lon2 - lon1)
    a = np.sin(dLat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dLon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return R * c

def sort_stations_nearest_neighbor(stations):
    # stations is a list of dicts: {'id': id, 'lat': lat, 'lng': lng, 'name': name}
    if not stations:
        return []
    
    # Start with the station that has the minimum longitude (likely an endpoint)
    # This is a heuristic. Actual lines can be complex (like circular Line 2).
    start_idx = min(range(len(stations)), key=lambda i: stations[i]['lng'])
    
    unvisited = stations[:]
    current = unvisited.pop(start_idx)
    sorted_path = [current]
    
    while unvisited:
        # Find nearest neighbor
        nearest_idx = min(range(len(unvisited)), 
                          key=lambda i: haversine(current['lat'], current['lng'], 
                                                  unvisited[i]['lat'], unvisited[i]['lng']))
        current = unvisited.pop(nearest_idx)
        sorted_path.append(current)
        
    return sorted_path

def process_subway_lines():
    print("Connecting to DB...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create target table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subway_lines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            line TEXT,
            coordinates_json TEXT
        )
    ''')
    cursor.execute('DELETE FROM subway_lines')
    
    # Read stations
    cursor.execute('SELECT id, line, name, lat, lng FROM subways WHERE lat IS NOT NULL AND lng IS NOT NULL')
    rows = cursor.fetchall()
    
    lines_dict = {}
    for r in rows:
        line_name = str(r[1]).strip()
        if not line_name:
            continue
        if line_name not in lines_dict:
            lines_dict[line_name] = []
        lines_dict[line_name].append({'id': r[0], 'name': r[2], 'lat': r[3], 'lng': r[4]})
        
    print(f"Found {len(lines_dict)} unique lines.")
    
    inserted = 0
    for line_name, stations in lines_dict.items():
        if len(stations) < 2:
            continue
        
        # Sort stations to form a continuous line
        sorted_stations = sort_stations_nearest_neighbor(stations)
        
        # Extract coordinates for Leaflet [[lat, lng], [lat, lng], ...]
        coords = [[s['lat'], s['lng']] for s in sorted_stations]
        
        cursor.execute('INSERT INTO subway_lines (line, coordinates_json) VALUES (?, ?)',
                       (line_name, json.dumps(coords)))
        inserted += 1
        
    conn.commit()
    conn.close()
    
    print(f"Successfully processed and stored {inserted} subway lines.")

if __name__ == '__main__':
    process_subway_lines()
