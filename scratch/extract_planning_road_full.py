import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/apply_complete_planning_upgrades.py', 'r', encoding='utf-8') as f:
    content = f.read()

pos = content.find("async function fetchPlanningRoads()")
if pos != -1:
    print(content[pos:pos+5500])
else:
    print("Not found")
