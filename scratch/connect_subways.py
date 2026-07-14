import sqlite3
import pandas as pd
import sys
import json
import numpy as np

DB_PATH = 'backend/data/map_data.db'

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

        cursor.execute('DELETE FROM subway_lines')
        
        cursor.execute('SELECT id, line, name, lat, lng, status FROM subways WHERE lat IS NOT NULL AND lng IS NOT NULL')
        rows = cursor.fetchall()
        
        # Group stations by line and status
        lines_dict = {}
        for r in rows:
            line_name = str(r[1]).strip()
            status = str(r[5]).strip()
            if not line_name:
                continue
            key = (line_name, status)
            if key not in lines_dict:
                lines_dict[key] = []
            lines_dict[key].append({'id': r[0], 'name': r[2], 'lat': r[3], 'lng': r[4], 'status': status})
            
        # For each "개발예정" line, find the closest station in the regular line to connect them
        for key, stations in list(lines_dict.items()):
            line_name, status = key
            if "예정" in status:
                # Find all regular stations for this line (use the largest group to avoid stray stations)
                reg_stations = []
                max_len = 0
                for k, v in lines_dict.items():
                    if k[0] == line_name and "예정" not in k[1]:
                        if len(v) > max_len:
                            max_len = len(v)
                            reg_stations = v
                
                if len(reg_stations) > 0:
                    # Find the closest regular station to any of the planned stations
                    min_dist = float('inf')
                    closest_reg_station = None
                    for p_station in stations:
                        for r_station in reg_stations:
                            dist = haversine(p_station['lat'], p_station['lng'], r_station['lat'], r_station['lng'])
                            if dist < min_dist:
                                min_dist = dist
                                closest_reg_station = r_station
                    if closest_reg_station:
                        stations.append(closest_reg_station)

        lines_inserted = 0
        for (line_name, status), stations in lines_dict.items():
            if len(stations) < 2:
                continue
            
            sorted_stations = sort_stations_nearest_neighbor(stations)
            coords = [[s['lat'], s['lng']] for s in sorted_stations]
            
            cursor.execute('INSERT INTO subway_lines (line, coordinates_json, status) VALUES (?, ?, ?)',
                           (line_name, json.dumps(coords), status))
            lines_inserted += 1
            
        print(f"Successfully processed and stored {lines_inserted} subway lines with connections.")

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
