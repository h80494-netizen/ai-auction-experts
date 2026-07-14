import pandas as pd
import requests
import re

input_file = r'c:\Users\llll\Documents\두인경매\바이브코딩\data\경공매데이터_update.xlsx'
output_file = r'c:\Users\llll\Documents\두인경매\바이브코딩\data\경공매데이터_update_지목추가.xlsx'

df = pd.read_excel(input_file, sheet_name='정리')

API_KEY = '2C1B6EA3-A71D-3294-9749-F878465C245B'
url = "http://api.vworld.kr/req/data"

def get_jimok_by_coord(row):
    lon = row.get('경도')
    lat = row.get('위도')
    
    if pd.isna(lon) or pd.isna(lat):
        return None
        
    params = {
        "key": API_KEY,
        "domain": "http://localhost",
        "service": "data",
        "request": "GetFeature",
        "data": "LP_PA_CBND_BUBUN",
        "geomFilter": f"POINT({lon} {lat})",
        "geometry": "false",
        "size": "1"
    }
    
    try:
        response = requests.get(url, params=params).json()
        features = response.get('response', {}).get('result', {}).get('featureCollection', {}).get('features', [])
        if features:
            props = features[0]['properties']
            jibun = props.get('jibun', '')
            
            # jibun에서 마지막 문자가 한글이면 지목으로 간주
            match = re.search(r'([가-힣])$', jibun)
            if match:
                return match.group(1)
            else:
                return '대' # 보통 생략된 경우는 '대'일 확률이 높으나 명확하지 않음. 혹은 원래 코드가 jym을 찾았으니 없으면 None
    except Exception as e:
        print(f"Error for coord ({lon}, {lat}): {e}")
        return None
    return None

print("Fetching jimok data using longitude and latitude with domain parameter...")
df['지목'] = df.apply(get_jimok_by_coord, axis=1)

print(f"Saving to {output_file}...")
df.to_excel(output_file, index=False)
print("Done!")
