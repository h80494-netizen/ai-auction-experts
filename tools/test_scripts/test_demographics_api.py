import sys
import os
import sqlite3

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app import get_map_demographics

# Coordinates for Gangnam-style busy area (highly dense commercial region)
lat, lng = 37.4979, 127.0276
print(f"Testing Demographics API Fallback for lat={lat}, lng={lng}...")

# Call the demographics endpoint function directly
# To force fallback, we will temporarily clear consumer_secret or mock it if needed,
# but let's check what it returns
res = get_map_demographics(lat, lng)

print("\n--- Demographics API Response ---")
import pprint
pprint.pprint(res)
