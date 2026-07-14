with open('backend/app.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_select = "SELECT id, name, geojson FROM redevelopment_zones"
new_select = "SELECT id, name, propel_cd, geojson FROM redevelopment_zones"

if old_select in code:
    code = code.replace(old_select, new_select)
    print("Replaced successfully!")
else:
    print("Not found, trying with alternative spacing or CRLF...")
    old_select_lf = old_select.replace('\n', '\r\n')
    if old_select_lf in code:
        code = code.replace(old_select_lf, new_select)
        print("Replaced with LF version!")
    else:
        print("Could not find the query target in app.py!")

with open('backend/app.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Modification of app.py complete!")
