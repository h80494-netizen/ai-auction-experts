import os

app_path = r'backend\app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

route_code = """
from naver_price_analyzer import analyze_price

class NaverPriceRequest(BaseModel):
    lat: float
    lon: float
    type: str
    area_pyeong: float
    floor: str
    total_floor: str
    build_year: str
    appraised_price: float
    min_price: float
    senior_debt: float

@app.post("/api/naver_price_analysis")
async def naver_price_analysis(req: NaverPriceRequest):
    try:
        result = analyze_price(
            target_lat=req.lat,
            target_lon=req.lon,
            target_type=req.type,
            target_area_pyeong=req.area_pyeong,
            target_floor=req.floor,
            target_total_floor=req.total_floor,
            target_build_year=req.build_year,
            target_appraised_price=req.appraised_price,
            target_min_price=req.min_price,
            target_senior_debt=req.senior_debt
        )
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

"""

# Insert before public_dir mount
target_str = 'public_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public")'
if target_str in content:
    content = content.replace(target_str, route_code + '\n' + target_str)
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Injected successfully")
else:
    print("Target string not found")
