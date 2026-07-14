import sqlite3
import os

backend_dir = os.path.abspath("backend")
DB_PATH = os.path.abspath(os.path.join(backend_dir, 'data', 'map_data.db'))

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

def test_query(property_types):
    query = "SELECT COUNT(*) FROM auctions WHERE 1=1"
    params = []
    
    types_list = property_types.split(',')
    type_clauses = []
    for t in types_list:
        if t == '아파트':
            type_clauses.append("property_type = '아파트'")
        elif t == '다세대':
            type_clauses.append("property_type = '다세대'")
        elif t == '오피스텔':
            type_clauses.append("property_type = '오피스텔'")
        elif t == '단독':
            type_clauses.append("property_type = '단독'")
        elif t == '지산':
            type_clauses.append("property_type = '지산'")
        elif t == '집합':
            type_clauses.append("property_type = '집합'")
        elif t == '일반':
            type_clauses.append("property_type = '일반'")
        elif t == '토지':
            type_clauses.append("property_type = '토지'")
        elif t == '공장':
            type_clauses.append("property_type = '공장'")
        elif t == '기타':
            type_clauses.append("(property_type NOT IN ('아파트', '다세대', '오피스텔', '단독', '지산', '집합', '일반', '토지', '공장'))")
        else:
            type_clauses.append("property_type = ?")
            params.append(t)
            
    if type_clauses:
        query += f" AND ({' OR '.join(type_clauses)})"
        
    cursor.execute(query, params)
    count = cursor.fetchone()[0]
    print(f"Filter '{property_types}' -> Query: {query} with {params} -> Count: {count}")

test_query("아파트")
test_query("지산")
test_query("집합")
test_query("일반")
test_query("지산,집합,일반")

conn.close()
