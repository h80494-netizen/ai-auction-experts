with open('backend/process_redevelopment_and_zoning.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace the create table statement
old_create = """        cursor.execute(f'''
            CREATE TABLE {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                min_lat REAL,
                max_lat REAL,
                min_lng REAL,
                max_lng REAL,
                geojson TEXT
            )
        ''')"""

new_create = """        cursor.execute(f'''
            CREATE TABLE {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                propel_cd TEXT,
                min_lat REAL,
                max_lat REAL,
                min_lng REAL,
                max_lng REAL,
                geojson TEXT
            )
        ''')"""

code = code.replace(old_create.replace('\r\n', '\n'), new_create.replace('\r\n', '\n'))
code = code.replace(old_create, new_create)

# Replace the insert statement
old_insert = """            # Use 'DGM_NM' as the name, fall back to index if not present
            name = str(row['DGM_NM']) if 'DGM_NM' in row else f"{table_name} {idx}"
            
            cursor.execute(f'''
                INSERT INTO {table_name} (name, min_lat, max_lat, min_lng, max_lng, geojson)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, min_lat, max_lat, min_lng, max_lng, geojson_str))"""

new_insert = """            # Use 'DGM_NM' as the name, fall back to index if not present
            name = str(row['DGM_NM']) if 'DGM_NM' in row else f"{table_name} {idx}"
            propel_cd = str(row['PROPEL_CD']) if 'PROPEL_CD' in row and row['PROPEL_CD'] is not None else None
            
            cursor.execute(f'''
                INSERT INTO {table_name} (name, propel_cd, min_lat, max_lat, min_lng, max_lng, geojson)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, propel_cd, min_lat, max_lat, min_lng, max_lng, geojson_str))"""

code = code.replace(old_insert.replace('\r\n', '\n'), new_insert.replace('\r\n', '\n'))
code = code.replace(old_insert, new_insert)

with open('backend/process_redevelopment_and_zoning.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Modification complete!")
