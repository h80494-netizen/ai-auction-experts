import sqlite3
import os
import random

db_path = 'backend/data/map_data.db'
if not os.path.exists(db_path):
    db_path = 'map_data.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Coordinates for a dense area in Seoul (e.g. Gangnam)
lat, lng = 37.4979, 127.0276
lat_delta = 0.015
lng_delta = 0.018

import math
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth's radius (m)
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# 1. Fetch commercial areas inside bounding box
cursor.execute('''
    SELECT name, population, category, lat, lng FROM commercial_areas
    WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?
''', (lat - lat_delta, lat + lat_delta, lng - lng_delta, lng + lng_delta))
comm_rows = cursor.fetchall()

total_comm_pop = 0
comm_count = 0
for row in comm_rows:
    dist = haversine_distance(lat, lng, row[3], row[4])
    if dist <= 1000:
        total_comm_pop += row[1]
        comm_count += 1

print(f"Location: ({lat}, {lng})")
print(f"Total commercial raw population sum within 1km: {total_comm_pop}")
print(f"Commercial area rows within 1km: {comm_count}")

# Scaled calculations (modified equations)
if total_comm_pop > 0:
    companies = comm_count * 8 + int(total_comm_pop * 0.0003) + 45
    workplace_pop = int(total_comm_pop * 0.005) + comm_count * 15 + 350
else:
    seed_val = int(lat*1000 + lng*1000)
    rng = random.Random(seed_val)
    companies = 35 + rng.randint(10, 50)
    workplace_pop = 250 + rng.randint(50, 250)

print(f"Scaled Workplace Population: {workplace_pop}")
print(f"Scaled Registered Companies: {companies}")

conn.close()
