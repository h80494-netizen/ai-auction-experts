import sqlite3

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def count_region(table, name_col=None, addr_col='address'):
    if addr_col:
        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {addr_col} LIKE '%경기%' OR {addr_col} LIKE '%경기도%'")
        gg_count = cursor.fetchone()[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {addr_col} LIKE '%인천%' OR {addr_col} LIKE '%인천광역시%'")
        ic_count = cursor.fetchone()[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {addr_col} LIKE '%서울%' OR {addr_col} LIKE '%서울특별시%'")
        se_count = cursor.fetchone()[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        tot = cursor.fetchone()[0]
        print(f"Table {table:20} -> Total: {tot:6} | Seoul: {se_count:5} | Gyeonggi: {gg_count:5} | Incheon: {ic_count:5}")
    else:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        tot = cursor.fetchone()[0]
        print(f"Table {table:20} -> Total: {tot:6} (No address column)")

count_region('subways', addr_col='address')
count_region('bus_stops', addr_col='address')
count_region('middle_schools', addr_col='address')
count_region('universities', addr_col='address')
count_region('auctions', addr_col='address')
count_region('commercial_areas', addr_col=None)
count_region('industrial_complexes', addr_col=None)

conn.close()
