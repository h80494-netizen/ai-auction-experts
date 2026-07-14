with open('backend/app.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_route = 'def get_property_issues(region: str = Query(..., description="Region to scan issues for")):'
new_route = 'def get_property_issues(region: str):'

if old_route in code:
    code = code.replace(old_route, new_route)
    print("Replaced Query definition!")
else:
    print("Not found exactly, trying with CRLF or spacing...")
    old_route_lf = old_route.replace('\n', '\r\n')
    if old_route_lf in code:
        code = code.replace(old_route_lf, new_route)
        print("Replaced LF Query definition!")
    else:
        print("Could not find Target!")

with open('backend/app.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Fix applied to app.py successfully!")
