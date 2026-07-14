import requests
import json

url = "http://localhost:8000/api/map/road_flows"

# Bounding box for testing (Seoul Jamsil/Songpa area)
base_params = {
    "min_lat": 37.510,
    "max_lat": 37.515,
    "min_lng": 127.070,
    "max_lng": 127.075
}

filters = [
    {"dayweek": "1", "tmzon": "00", "agrde": "00", "desc": "주중, 전체시간, 전체연령 (기준)"},
    {"dayweek": "2", "tmzon": "04", "agrde": "20", "desc": "주말, 저녁(17-21시), 20대 (상업가 피크)"},
    {"dayweek": "2", "tmzon": "06", "agrde": "60", "desc": "주말, 새벽(24-06시), 60대 이상 (심야 실버)"}
]

print("=== [TEST] Parametric Road Flows API Verification ===")

results = []

for filt in filters:
    params = base_params.copy()
    params["dayweek"] = filt["dayweek"]
    params["tmzon"] = filt["tmzon"]
    params["agrde"] = filt["agrde"]
    
    print(f"\nRequesting: {filt['desc']} ...")
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            res_data = response.json()
            features = res_data.get("data", {}).get("features", [])
            print(f"-> Successfully returned {len(features)} road segments.")
            if features:
                # Calculate average flow
                flows = [f.get("properties", {}).get("avg_hourly_flow", 0) for f in features]
                avg_flow_val = sum(flows) / len(flows)
                max_flow_val = max(flows)
                min_flow_val = min(flows)
                print(f"   Average Flow: {avg_flow_val:.1f}명/시간")
                print(f"   Max Flow: {max_flow_val}명/시간, Min Flow: {min_flow_val}명/시간")
                results.append({
                    "desc": filt["desc"],
                    "avg_flow": avg_flow_val,
                    "max_flow": max_flow_val
                })
        else:
            print(f"-> Failed with status code {response.status_code}")
    except Exception as e:
        print(f"-> Request failed: {e}")

print("\n=== [SUMMARY] ===")
for r in results:
    print(f"{r['desc']} => Average Flow: {r['avg_flow']:.1f}명/시간, Max: {r['max_flow']}명/시간")
