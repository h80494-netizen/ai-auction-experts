import requests

url = "http://localhost:8000/api/search_cases"
data = {"case_number": "2024타경6060"}

try:
    print("Querying /api/search_cases for 2024타경6060...")
    response = requests.post(url, json=data)
    print("Status Code:", response.status_code)
    print("Response JSON:")
    print(response.json())
except Exception as e:
    print("Error calling API:", e)
