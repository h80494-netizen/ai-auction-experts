import requests
import json
st = requests.get('http://127.0.0.1:8000/api/analyze/status/1d8aabd6-0428-4f9f-9417-18bd17f9472d').json()
with open('error_out.txt', 'w', encoding='utf-8') as f:
    f.write(st['data']['analysis'])
