import sqlite3
import math
from collections import Counter

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get Gyeonggi auctions
cursor.execute("SELECT lat, lng FROM auctions WHERE address LIKE '%경기%'")
auctions = cursor.fetchall()

# Count auctions in each cell
cell_counts = Counter()
for lat, lng in auctions:
    if lat is None or lng is None:
        continue
    lat_idx = int(math.floor(lat / 0.01))
    lng_idx = int(math.floor(lng / 0.01))
    cell_counts[(lat_idx, lng_idx)] += 1

# Check which ones are already cached
cursor.execute("SELECT lat_idx, lng_idx FROM road_cache_grids")
cached_cells = set(cursor.fetchall())

uncached_counts = {cell: count for cell, count in cell_counts.items() if cell not in cached_cells}
sorted_uncached = sorted(uncached_counts.items(), key=lambda x: x[1], reverse=True)

print(f"Total uncached Gyeonggi cells: {len(sorted_uncached)}")
print("\nTop 20 dense uncached Gyeonggi cells:")
for cell, count in sorted_uncached[:20]:
    print(f"Cell {cell}: {count} auctions")

# Calculate cumulative coverage
total_auctions = sum(cell_counts.values())
covered_auctions_cached = sum(count for cell, count in cell_counts.items() if cell in cached_cells)
print(f"\nAuctions in currently cached cells: {covered_auctions_cached} ({covered_auctions_cached/total_auctions*100:.2f}%)")

running_total = covered_auctions_cached
coverage_milestones = [0.5, 0.7, 0.8, 0.9, 0.95]
milestone_idx = 0
for idx, (cell, count) in enumerate(sorted_uncached):
    running_total += count
    ratio = running_total / total_auctions
    if milestone_idx < len(coverage_milestones) and ratio >= coverage_milestones[milestone_idx]:
        print(f"Reached {coverage_milestones[milestone_idx]*100}% coverage after caching {idx+1} more cells (total cells to cache: {idx+1})")
        milestone_idx += 1

conn.close()
