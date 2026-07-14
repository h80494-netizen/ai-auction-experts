import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/apply_complete_planning_upgrades.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re
# Let's find matches of HTML sections or replacements
# E.g. search for strings that contain 'toggle-zoning' or 'zoning-sub-container'
lines = content.split('\n')
print("Searching for zoning/planning road HTML references in scratch/apply_complete_planning_upgrades.py:")
for idx, line in enumerate(lines):
    if 'toggle-zoning' in line or 'toggle-planning-road' in line or 'zoning-sub-container' in line or 'planning-road-sub-container' in line:
        print(f"  Line {idx+1}: {line.strip()[:150]}")
