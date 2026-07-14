with open('public/map.html', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if "<!-- Left Panel: Layer List -->" in line:
        start_idx = i
    if "<!-- Leaflet JS -->" in line:
        end_idx = i
        break

print(f"start_idx = {start_idx}, end_idx = {end_idx}")
if start_idx != -1 and end_idx != -1:
    print(f"Lines to be replaced: {end_idx - start_idx}")
    print("Is 'toggle-gmr-pop-road' in target block in replace_panels.py?")
    with open('replace_panels.py', encoding='utf-8') as f:
        rp_content = f.read()
    if 'toggle-gmr-pop-road' in rp_content:
        print("  Yes, it is in replace_panels.py!")
    else:
        print("  NO, IT IS NOT IN REPLACE_PANELS.PY!")
