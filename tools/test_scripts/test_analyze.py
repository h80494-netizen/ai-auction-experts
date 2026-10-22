import requests
import time

res = requests.post('http://127.0.0.1:8000/api/analyze', json={
    "case_number": "2025 타경 102495",
    "address_hint": "서울 은평구 구산동",
    "property_type": "아파트",
    "house_count": 1,
    "investor_type": "보수적",
    "investment_duration": "단기",
    "target_return_rate": 20.0,
    "is_regulated_area": False,
    "calculated_aging": "20년차",
    "madangs_url": ""
})
data = res.json()
print("Init:", data)

if data['status'] == 'processing':
    task_id = data['task_id']
    for _ in range(10):
        time.sleep(5)
        st = requests.get(f'http://127.0.0.1:8000/api/analyze/status/{task_id}').json()
        print("Status:", st['status'])
        if st['status'] != 'processing':
            if 'data' in st and 'analysis' in st['data']:
                print("Error text snippet:", st['data']['analysis'][:200])
            else:
                print("Result:", st)
            break
