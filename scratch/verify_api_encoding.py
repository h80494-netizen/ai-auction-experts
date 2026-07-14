import urllib.request
import json

url = "http://localhost:8000/api/map/road_flows?min_lat=37.48&max_lat=37.51&min_lng=127.01&max_lng=127.04"
try:
    print(f"Fetching from {url}...")
    response = urllib.request.urlopen(url, timeout=20)
    data = json.loads(response.read().decode('utf-8'))
    
    # Save the output as UTF-8 file
    out_file = "scratch/api_response_sample.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully saved sample response to {out_file}.")
    features = data.get("data", {}).get("features", [])
    if features:
        print("First feature properties in Python memory:")
        print("road_name:", features[0]["properties"].get("road_name"))
        print("road_class:", features[0]["properties"].get("road_class"))
        print("flow_type:", features[0]["properties"].get("flow_type"))
except Exception as e:
    print("Verification failed:", e)
