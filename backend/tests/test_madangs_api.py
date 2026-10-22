import asyncio
import httpx

async def test():
    async with httpx.AsyncClient(timeout=60.0) as client:
        print("1. Search API 호출 (2025-0800-059271)")
        res = await client.post("http://localhost:8000/api/search_cases", json={"case_number": "2025-0800-059271"})
        print("Search Result:", res.json())
        
        if res.json().get("status") == "success":
            print("\n2. Analyze API 호출")
            analyze_payload = {
                "case_number": "2025-0800-059271",
                "address_hint": "",
                "property_type": "상가",
                "house_count": 0,
                "investor_type": "보수적",
                "investment_duration": "단기",
                "target_return_rate": 15,
                "repair_condition": "양호",
                "is_regulated_area": False,
                "madangs_url": ""
            }
            res2 = await client.post("http://localhost:8000/api/analyze", json=analyze_payload)
            print("Analyze Init Result:", res2.json())
            task_id = res2.json().get("task_id")
            
            while True:
                await asyncio.sleep(5)
                status_res = await client.get(f"http://localhost:8000/api/analyze/status/{task_id}")
                status_data = status_res.json()
                print("Status:", status_data["status"], "| Message:", status_data.get("message", ""))
                if status_data["status"] != "processing":
                    print("Final Data keys:", status_data.get("data", {}).keys())
                    break

if __name__ == "__main__":
    asyncio.run(test())
