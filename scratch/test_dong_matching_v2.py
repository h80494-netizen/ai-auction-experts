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

# Get all bus stops
cursor.execute("SELECT name, city, lat, lng, address FROM bus_stops WHERE lat IS NOT NULL AND lng IS NOT NULL")
bus_stops = cursor.fetchall()

matched = 0
unmatched = []

for sgg, dong in dongs:
    dong_clean = re.sub(r'\d+동$', '동', dong)
    dong_base = dong.replace('동', '')
    
    # 1. Try auctions
    matching_coords = []
    for addr, lat, lng in auctions:
        if sgg in addr and (dong in addr or dong_clean in addr or dong_base in addr):
            matching_coords.append((lat, lng))
            
    if matching_coords:
        matched += 1
        continue
        
    # 2. Try bus stops
    matching_bus = []
    for name, city, lat, lng, addr in bus_stops:
        if sgg in city and (dong in name or dong in addr or dong_clean in addr or dong_base in addr):
            matching_bus.append((lat, lng))
            
    if matching_bus:
        matched += 1
    else:
        unmatched.append((sgg, dong))

print(f"Matched {matched} out of {len(dongs)} using auctions + bus_stops!")
print(f"Remaining unmatched ({len(unmatched)}):")
for sgg, dong in unmatched:
    print(f"  {sgg} {dong}")
