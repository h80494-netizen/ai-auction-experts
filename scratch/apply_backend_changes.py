import os

app_path = 'backend/app.py'
if not os.path.exists(app_path):
    print("Error: backend/app.py not found")
    exit(1)

with open(app_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Define new APIs to inject
new_apis = """            "commercial_areas": commercial_areas
        }
    }


@app.get("/api/map/redevelopment_zones")
def get_map_redevelopment_zones(
    min_lat: Optional[float] = None,
    max_lat: Optional[float] = None,
    min_lng: Optional[float] = None,
    max_lng: Optional[float] = None
):
    if not os.path.exists(DB_PATH):
        return {"status": "error", "message": "DB not found"}
        
    if not (min_lat and max_lat and min_lng and max_lng):
        return {"status": "success", "data": []}
        
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='redevelopment_zones'")
    if not cursor.fetchone():
        conn.close()
        return {"status": "success", "data": []}
        
    query = '''
        SELECT id, name, propel_cd, geojson FROM redevelopment_zones
        WHERE max_lat >= ? AND min_lat <= ? 
          AND max_lng >= ? AND min_lng <= ?
        LIMIT 1000
    '''
    cursor.execute(query, (min_lat, max_lat, min_lng, max_lng))
    data = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return {"status": "success", "data": data}


@app.get("/api/map/crosswalks")
def get_map_crosswalks(
    min_lat: Optional[float] = None,
    max_lat: Optional[float] = None,
    min_lng: Optional[float] = None,
    max_lng: Optional[float] = None
):
    import json
    if not os.path.exists(DB_PATH):
        return {"status": "error", "message": "DB not found"}
        
    if not (min_lat and max_lat and min_lng and max_lng):
        return {"status": "success", "data": {"type": "FeatureCollection", "features": []}}
        
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='crosswalk_segments'")
    if not cursor.fetchone():
        conn.close()
        return {"status": "success", "data": {"type": "FeatureCollection", "features": []}}
        
    cursor.execute('''
        SELECT name, coords_json FROM crosswalk_segments
        WHERE max_lat >= ? AND min_lat <= ? 
          AND max_lng >= ? AND min_lng <= ?
        LIMIT 1500
    ''', (min_lat, max_lat, min_lng, max_lng))
    
    rows = cursor.fetchall()
    features = []
    
    for r in rows:
        name, coords_json = r['name'], r['coords_json']
        try:
            coords = json.loads(coords_json)
        except Exception:
            continue
            
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": coords
            },
            "properties": {
                "name": name,
                "highway": "횡단보도"
            }
        })
        
    conn.close()
    
    geojson_result = {
        "type": "FeatureCollection",
        "features": features
    }
    
    return {"status": "success", "data": geojson_result}


@app.get("/api/map/hagwon_polygons")"""

# Anchor to replace
target_anchor = """            "commercial_areas": commercial_areas
        }
    }

@app.get("/api/map/hagwon_polygons")"""

# 2. Modify app.py: insert APIs
if target_anchor in code:
    code = code.replace(target_anchor, new_apis)
    print("Successfully injected new API routes.")
else:
    # Try alternative spacing or CRLF version
    target_anchor_lf = target_anchor.replace('\r\n', '\n')
    new_apis_lf = new_apis.replace('\r\n', '\n')
    if target_anchor_lf in code:
        code = code.replace(target_anchor_lf, new_apis_lf)
        print("Successfully injected new API routes (LF version).")
    else:
        print("Failed to find target anchor for APIs!")
        exit(1)

# 3. Replace road flows query (exclude crosswalks)
old_query = """        # 캐시 DB로부터 영역 매칭 도로망 가져오기
        cursor.execute('''
            SELECT name, highway, width, coords_json FROM road_cache_segments
            WHERE max_lat >= ? AND min_lat <= ? AND max_lng >= ? AND min_lng <= ?
        ''', (min_lat, max_lat, min_lng, max_lng))"""

new_query = """        # 캐시 DB로부터 영역 매칭 도로망 가져오기
        cursor.execute('''
            SELECT name, highway, width, coords_json FROM road_cache_segments
            WHERE max_lat >= ? AND min_lat <= ? AND max_lng >= ? AND min_lng <= ?
              AND highway != '횡단보도'
        ''', (min_lat, max_lat, min_lng, max_lng))"""

if old_query in code:
    code = code.replace(old_query, new_query)
    print("Successfully updated road flows query.")
else:
    old_query_lf = old_query.replace('\r\n', '\n')
    new_query_lf = new_query.replace('\r\n', '\n')
    if old_query_lf in code:
        code = code.replace(old_query_lf, new_query_lf)
        print("Successfully updated road flows query (LF version).")
    else:
        print("Failed to find road flows query to replace!")
        exit(1)

# 4. Save file
with open(app_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Backend modification complete!")
