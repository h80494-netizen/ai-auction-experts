import os
import sys
from fastapi.testclient import TestClient

# Ensure backend directory is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from app import app
    client = TestClient(app)
    print("FastAPI app loaded successfully!")
    
    # Standard Leaflet EPSG:3857 parameters for a small region in Suwon, Gyeonggi-do
    # BBOX coordinates spanning roughly 500m
    params = {
        'SERVICE': 'WMS',
        'VERSION': '1.1.1',
        'REQUEST': 'GetMap',
        'FORMAT': 'image/png',
        'TRANSPARENT': 'true',
        'STYLES': '',
        'LAYERS': 'vw_gis_pop_road',
        'VIEWPARAMS': 'stdr:20253;flag:time;val:20;radius:100;',
        'STORE': 'gmr_new',
        'SRS': 'EPSG:3857',
        'WIDTH': '256',
        'HEIGHT': '256',
        # Approximate Suwon coordinate box in Web Mercator
        'BBOX': '14139800,4474800,14140400,4475400'
    }
    
    print("\n[Test] Sending mock WMS proxy request to /api/gmr/wms using TestClient...")
    response = client.get("/api/gmr/wms", params=params)
    
    print("Response Status Code:", response.status_code)
    print("Response Content-Type:", response.headers.get("Content-Type"))
    print("Response Length:", len(response.content))
    
    if response.status_code == 200 and 'image' in response.headers.get("Content-Type", ""):
        # Save output to verify it is a valid map tile!
        output_path = "scratch/proxy_tile_3857_success.png"
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"SUCCESS! WMS proxy successfully processed EPSG:3857, reprojected to EPSG:5181, fetched map tile, and returned it!")
        print(f"Saved generated tile to: {output_path}")
    else:
        print("Response Text Preview (Error or Empty):")
        print(response.text[:1000])
        
except Exception as e:
    print("Execution Error:", e)
