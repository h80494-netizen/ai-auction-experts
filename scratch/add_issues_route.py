with open('backend/app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Let's find a good insertion point, e.g. before the end of the file or near other endpoints
# Let's insert it before "@app.get("/api/map/zoning")"
target = '@app.get("/api/map/zoning")'
route_code = """@app.get("/api/issues")
def get_property_issues(region: str = Query(..., description="Region to scan issues for")):
    try:
        from crawler.issue_scanner import scan_region_issues
        issues = scan_region_issues(region)
        return {"status": "success", "data": issues}
    except Exception as e:
        return {"status": "error", "message": str(e)}

"""

if target in code:
    code = code.replace(target, route_code + target)
    print("Successfully added /api/issues endpoint to app.py")
else:
    print("Could not find zoning endpoint, appending at the bottom...")
    code += "\n" + route_code

with open('backend/app.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Modification of app.py complete!")
