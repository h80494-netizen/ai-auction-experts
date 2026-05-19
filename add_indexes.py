import sqlite3

def add_indexes():
    db_path = 'backend/data/map_data.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    tables = [
        ('subways', ['lat', 'lng']),
        ('universities', ['lat', 'lng']),
        ('middle_schools', ['lat', 'lng']),
        ('industrial_complexes', ['lat', 'lng']),
        ('bus_stops', ['lat', 'lng']),
        ('commercial_areas', ['lat', 'lng']),
        ('population_grids', ['lat', 'lng'])
    ]
    
    print("Adding spatial indexes...")
    for table, columns in tables:
        try:
            # Check if table exists
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if cursor.fetchone():
                idx_name = f"idx_{table}_{'_'.join(columns)}"
                cols = ', '.join(columns)
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({cols})")
                print(f"Created index {idx_name} on {table}")
            else:
                print(f"Table {table} does not exist.")
        except Exception as e:
            print(f"Error on {table}: {e}")
            
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='district_units'")
        if cursor.fetchone():
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_district_units_bounds ON district_units(max_lat, min_lat, max_lng, min_lng)")
            print("Created index idx_district_units_bounds")
    except Exception as e:
        print(f"Error on district_units: {e}")

    conn.commit()
    conn.close()
    print("Done!")

if __name__ == '__main__':
    add_indexes()
