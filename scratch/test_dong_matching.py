import pandas as pd
import sqlite3
import re

df_pop = pd.read_excel('data/경기유동인구_행정동단위집계.xls')
dongs = df_pop[['시군구명', '행정동명']].drop_duplicates().values.tolist()

conn = sqlite3.connect('backend/data/map_data.db')
cursor = conn.cursor()

# Get all auctions
cursor.execute("SELECT address, lat, lng FROM auctions WHERE lat IS NOT NULL AND lng IS NOT NULL")
auctions = cursor.fetchall()

matched = 0
unmatched = []

for sgg, dong in dongs:
    # Try to find auction in this sgg and dong
    # Remove numbers from dong for fuzzy matching (e.g., '망포2동' -> '망포')
    dong_clean = re.sub(r'\d+동$', '동', dong)
    dong_base = dong.replace('동', '')
    
    # We can filter auctions
    matching_auctions = []
    for addr, lat, lng in auctions:
        if sgg in addr and (dong in addr or dong_clean in addr or dong_base in addr):
            matching_auctions.append((lat, lng))
            
    if matching_auctions:
        matched += 1
    else:
        unmatched.append((sgg, dong))

print(f"Matched {matched} out of {len(dongs)}")
print("Unmatched samples:")
for sgg, dong in unmatched[:20]:
    print(f"  {sgg} {dong}")
