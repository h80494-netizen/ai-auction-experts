import sqlite3

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT propel_cd, name FROM redevelopment_zones")
rows = cursor.fetchall()

def get_redevelopment_stage(propel_cd):
    if not propel_cd:
        return '초기'
    code = propel_cd.upper()
    
    # 후기 단계
    late_prefixes = ['PP06', 'PP07', 'PP08', 'PP09', 'PP19', 'PP20']
    is_late_prefix = any(code.startswith(p) for p in late_prefixes)
    late_specific_codes = [
        'PP1111', 'PP1112', 'PP1113', 
        'PP1206', 'PP1207', 'PP1208', 'PP1209', 
        'PP1306', 
        'PP1406', 'PP1407', 
        'PP1505', 'PP1506', 'PP1507', 
        'PP1604', 
        'PP1809', 'PP1810',
        'PP0209', 'PP0210', 'PP0211', 'PP0504', 'PP0505'
    ]
    if is_late_prefix or (code in late_specific_codes):
        return '후기'
        
    # 중기 단계
    middle_prefixes = ['PP04', 'PP05']
    is_middle_prefix = any(code.startswith(p) for p in middle_prefixes)
    middle_specific_codes = [
        'PP0208', 'PP0305', 'PP1110', 
        'PP1401', 'PP1402', 'PP1403', 'PP1404', 'PP1405', 
        'PP1501', 'PP1502', 'PP1503', 'PP1504'
    ]
    if is_middle_prefix or (code in middle_specific_codes):
        return '중기'
        
    return '초기'

counts = {'초기': 0, '중기': 0, '후기': 0}
stage_by_code = {}

for propel_cd, name in rows:
    stage = get_redevelopment_stage(propel_cd)
    counts[stage] += 1
    if stage not in stage_by_code:
        stage_by_code[stage] = []
    if propel_cd not in [x[0] for x in stage_by_code[stage]]:
        stage_by_code[stage].append((propel_cd, name))

print("Current counts:")
print(counts)

print("\nSome sample codes in '초기':")
for pc, name in stage_by_code['초기'][:15]:
    print(f"  {pc}: {name}")

print("\nSome sample codes in '중기':")
for pc, name in stage_by_code['중기'][:15]:
    print(f"  {pc}: {name}")

print("\nSome sample codes in '후기':")
for pc, name in stage_by_code['후기'][:15]:
    print(f"  {pc}: {name}")

conn.close()
