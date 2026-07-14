import sqlite3
import os

db_path = os.path.abspath(os.path.join('backend', 'data', 'map_data.db'))
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Noryangjin target mappings
updates = {
    '노량진1': 'PP1111', # 중기 (사업시행인가)
    '노량진1구역': 'PP1111',
    '노량진2': 'PP1112', # 후기 (이주/철거/착공)
    '노량진2구역': 'PP1112',
    '노량진3': 'PP1111', # 중기 (사업시행인가)
    '노량진3구역': 'PP1111',
    '노량진4': 'PP1112', # 후기 (관리처분인가/이주)
    '노량진4구역': 'PP1112',
    '노량진5': 'PP1111', # 중기 (사업시행인가)
    '노량진5구역': 'PP1111',
    '노량진6': 'PP1112', # 후기 (이주/철거/착공)
    '노량진6구역': 'PP1112',
    '노량진7': 'PP1112', # 후기 (관리처분인가)
    '노량진7구역': 'PP1112',
    '노량진8': 'PP1112', # 후기 (이주/철거)
    '노량진8구역': 'PP1112',
}

for name, code in updates.items():
    query = "UPDATE redevelopment_zones SET propel_cd = ? WHERE name = ?"
    cursor.execute(query, (code, name))
    print(f"Updated {name} to {code}. Rows affected: {cursor.rowcount}")

conn.commit()
conn.close()
